from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from apps.attributes.models import Attribute
from apps.attributes.serializers import AttributeSerializer
from apps.attribute_values.models import AttributeValue
from django.utils.dateparse import parse_date

class AttributeListCreateView(APIView):
    # GET requests to fetch all non-deleted attributes with optional status filter
    @transaction.atomic
    def get(self, request):
        try:
            attributes = Attribute.objects.filter(attributes_is_deleted=False)
            
            status_filter = request.GET.get('attributes_status')
            if status_filter is not None:
                if status_filter.lower() == 'true':
                    attributes = attributes.filter(attributes_is_active=True)
                elif status_filter.lower() == 'false':
                    attributes = attributes.filter(attributes_is_active=False)

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
                                attributes = attributes.filter(
                                    attributes_created_at__date__gte=start_date,
                                    attributes_created_at__date__lte=end_date
                                )
                            else:
                                return Response({
                                    "success": False,
                                    "status": 400,
                                    "message": "Invalid date range format. Use 'YYYY-MM-DD to YYYY-MM-DD' with valid dates",
                                    "error": "Invalid date format in range"
                                }, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({
                                "success": False,
                                "status": 400,
                                "message": "Invalid date range format. Use 'YYYY-MM-DD to YYYY-MM-DD'",
                                "error": "Invalid range format"
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    elif '-' in created_at_param and created_at_param.count('-') >= 2:
                        filter_date = parse_date(created_at_param)
                        if filter_date:
                            attributes = attributes.filter(attributes_created_at__date=filter_date)
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
            
            
            serializer = AttributeSerializer(attributes, many=True)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched all attribute data successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST requests to create a new attribute
    @transaction.atomic
    def post(self, request):
        try:
            serializer = AttributeSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 201,
                    "message": "Attribute created successfully",
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
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttributeDetailView(APIView):
    # Retrieve attribute by ID if not soft deleted
    @transaction.atomic
    def get(self, request, attributes_id):
        try:
            attribute = Attribute.objects.get(attributes_id=attributes_id, attributes_is_deleted=False)
            serializer = AttributeSerializer(attribute)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched Attribute by ID Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Attribute not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update the attribute
    @transaction.atomic
    def put(self, request, attributes_id):
        try:
            attribute = Attribute.objects.get(attributes_id=attributes_id, attributes_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Attribute not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = AttributeSerializer(attribute, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Attribute updated successfully",
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
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Mark the attribute as soft deleted
    @transaction.atomic
    def delete(self, request, attributes_id):
        try:
            attribute = Attribute.objects.get(attributes_id=attributes_id, attributes_is_deleted=False)
            attribute.attributes_is_deleted = True
            attribute.save()

            # Soft-deletes related Attribute Values objects.
            AttributeValue.objects.filter(
                attribute_values_attributes_id=attribute,
                attribute_values_is_deleted=False
            ).update(attribute_values_is_deleted=True)

            return Response({
                "success": True,
                "status": 200,
                "message": "Attribute deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Attribute not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
