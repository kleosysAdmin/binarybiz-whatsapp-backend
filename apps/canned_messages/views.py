from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from apps.canned_messages.models import CannedMessage
from apps.canned_messages.serializers import CannedMessageSerializer, CannedMessageFavouriteSerializer
from django.utils.dateparse import parse_date

class CannedMessageListCreateView(APIView):
    # GET requests to fetch all non-deleted messages with filters
    @transaction.atomic
    def get(self, request):
        try:
            messages = CannedMessage.objects.filter(canned_messages_is_deleted=False)
            
            # Filter by message type
            message_type = request.GET.get('canned_messages_type')
            if message_type:
                messages = messages.filter(canned_messages_type=message_type)
            
            # Filter by favourite status
            is_favourite = request.GET.get('is_favourite')
            if is_favourite is not None:
                if is_favourite.lower() == 'true':
                    messages = messages.filter(canned_messages_is_favourite=True)
                elif is_favourite.lower() == 'false':
                    messages = messages.filter(canned_messages_is_favourite=False)
            

            #  Filter by Date
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
                                messages = messages.filter(
                                    canned_messages_created_at__date__gte=start_date,
                                    canned_messages_created_at__date__lte=end_date
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
                            messages = messages.filter(canned_messages_created_at__date=filter_date)
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


            serializer = CannedMessageSerializer(messages, many=True)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched all canned messages successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST requests to create a new canned message
    @transaction.atomic
    def post(self, request):
        try:
            serializer = CannedMessageSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 201,
                    "message": "Canned message created successfully",
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


class CannedMessageDetailView(APIView):
    # Retrieve message by ID if not soft deleted
    @transaction.atomic
    def get(self, request, canned_messages_id):
        try:
            message = CannedMessage.objects.get(canned_messages_id=canned_messages_id, canned_messages_is_deleted=False)
            serializer = CannedMessageSerializer(message)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched Canned Message by ID Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Canned Message not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update the canned message
    @transaction.atomic
    def put(self, request, canned_messages_id):
        try:
            message = CannedMessage.objects.get(canned_messages_id=canned_messages_id, canned_messages_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Canned Message not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = CannedMessageSerializer(message, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Canned message updated successfully",
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

    # Mark the canned message as soft deleted
    @transaction.atomic
    def delete(self, request, canned_messages_id):
        try:
            message = CannedMessage.objects.get(canned_messages_id=canned_messages_id, canned_messages_is_deleted=False)
            message.canned_messages_is_deleted = True
            message.save()

            return Response({
                "success": True,
                "status": 200,
                "message": "Canned message deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Canned Message not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CannedMessageFavouriteView(APIView):
    # Update favourite status only
    @transaction.atomic
    def put(self, request, canned_messages_id):
        try:
            message = CannedMessage.objects.get(canned_messages_id=canned_messages_id, canned_messages_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Canned Message not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = CannedMessageFavouriteSerializer(message, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Favourite status updated successfully",
                    "data": {
                        "canned_messages_id": message.canned_messages_id,
                        "canned_messages_name": message.canned_messages_name,
                        "canned_messages_is_favourite": message.canned_messages_is_favourite,
                        "canned_messages_type": message.canned_messages_type,
                        "canned_messages_description": message.canned_messages_description,
                    }
                }, status=status.HTTP_200_OK)
            
            error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Invalid request for favourite update."
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