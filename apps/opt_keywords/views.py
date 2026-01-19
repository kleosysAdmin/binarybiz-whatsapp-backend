from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date

from apps.opt_keywords.models import OptKeyword
from apps.opt_keywords.serializers import OptKeywordSerializer


class OptKeywordListCreateView(APIView):
    # List all opt keyword configurations
    @transaction.atomic
    def get(self, request):
        try:
            opt_keywords = OptKeyword.objects.filter(opt_keywords_is_deleted=False)
            
            # Filter by type
            type_filter = request.GET.get('type')
            if type_filter:
                if type_filter.lower() in ['opt_in', 'opt_out']:
                    opt_keywords = opt_keywords.filter(opt_keywords_type=type_filter.lower())
                else:
                    return Response({
                        "success": False,
                        "status": 400,
                        "message": "Invalid type filter. Use 'opt_in' or 'opt_out'",
                        "error": "Invalid filter value"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Date filtering for created_at
            created_at_param = request.GET.get('created_at')
            if created_at_param:
                try:
                    if 'to' in created_at_param.lower():
                        date_parts = created_at_param.lower().split('to')
                        if len(date_parts) == 2:
                            start_date_str = date_parts[0].strip()
                            end_date_str = date_parts[1].strip()
                            
                            start_date = parse_date(start_date_str)
                            end_date = parse_date(end_date_str)
                            
                            if start_date and end_date:
                                opt_keywords = opt_keywords.filter(
                                    opt_keywords_created_at__date__gte=start_date,
                                    opt_keywords_created_at__date__lte=end_date
                                )
                            else:
                                return Response({
                                    "success": False,
                                    "status": 400,
                                    "message": "Invalid date range format. Use 'YYYY-MM-DD to YYYY-MM-DD' with valid dates",
                                    "error": "Invalid date format"
                                }, status=status.HTTP_400_BAD_REQUEST)
                    
                    elif '-' in created_at_param and created_at_param.count('-') >= 2:
                        filter_date = parse_date(created_at_param)
                        if filter_date:
                            opt_keywords = opt_keywords.filter(opt_keywords_created_at__date=filter_date)
                        else:
                            return Response({
                                "success": False,
                                "status": 400,
                                "message": "Invalid date format. Use 'YYYY-MM-DD'",
                                "error": "Invalid date format"
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        return Response({
                            "success": False,
                            "status": 400,
                            "message": "Invalid date parameter. Use 'YYYY-MM-DD' for single date or 'YYYY-MM-DD to YYYY-MM-DD' for range",
                            "error": "Invalid date parameter format"
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except ValueError as e:
                    return Response({
                        "success": False,
                        "status": 400,
                        "message": "Invalid date value",
                        "error": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({
                        "success": False,
                        "status": 400,
                        "message": "Error processing date filter",
                        "error": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = OptKeywordSerializer(opt_keywords, many=True)
            
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched all opt keyword configurations successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Create opt keyword configuration
    @transaction.atomic
    def post(self, request):
        try:
            serializer = OptKeywordSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    "success": True,
                    "status": 201,
                    "message": f"opt keywords saved successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Invalid request."
            return Response({
                "success": False,
                "status": 400,
                "message": "Invalid Input",
                "error": error_message
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OptKeywordDetailView(APIView):
    
    # Update the opt keyword configuration
    @transaction.atomic
    def put(self, request, opt_type):
        try:
            if opt_type.lower() not in ['opt_in', 'opt_out']:
                return Response({
                    "success": False,
                    "status": 400,
                    "error": "Invalid opt type. Use 'opt_in' or 'opt_out'"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            opt_keyword = OptKeyword.objects.get(
                opt_keywords_type=opt_type.lower(),
                opt_keywords_is_deleted=False
            )
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": f"{opt_type.replace('_', '-').title()} configuration not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = OptKeywordSerializer(opt_keyword, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Opt Keyword Updated Successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            
            error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Invalid request for update."
            return Response({
                "success": False,
                "status": 400,
                "error": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Mark the opt keyword configuration as soft deleted
    @transaction.atomic
    def delete(self, request, opt_type):
        try:
            if opt_type.lower() not in ['opt_in', 'opt_out']:
                return Response({
                    "success": False,
                    "status": 400,
                    "error": "Invalid opt type. Use 'opt_in' or 'opt_out'"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            opt_keyword = OptKeyword.objects.get(
                opt_keywords_type=opt_type.lower(),
                opt_keywords_is_deleted=False
            )
            opt_keyword.opt_keywords_is_deleted = True
            opt_keyword.save()

            return Response({
                "success": True,
                "status": 200,
                "message": f"{opt_keyword.get_opt_keywords_type_display()} configuration deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": f"{opt_type.replace('_', '-').title()} configuration not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)