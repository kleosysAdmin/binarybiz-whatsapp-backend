from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from apps.profile_chat_settings.models import ProfileChatSettings, WorkingHours
from apps.profile_chat_settings.serializers import (
    ProfileChatSettingsSerializer, 
    ProfileChatSettingsResponseSerializer
)


class ProfileChatSettingsDetailView(APIView):
    # GET - Retrieve profile chat settings by ID
    @transaction.atomic
    def get(self, request, profile_chat_settings_id):
        try:
            instance = ProfileChatSettings.objects.get(
                profile_chat_settings_id=profile_chat_settings_id,
                profile_chat_settings_is_deleted=False
            )
            
            serializer = ProfileChatSettingsResponseSerializer(
                instance, 
                context={'request': request}
            )
            
            return Response({
                "success": True,
                "status": 200,
                "message": "Profile chat settings fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Profile chat settings not found"
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # PUT - Update profile chat settings with transaction
    @transaction.atomic
    def put(self, request, profile_chat_settings_id):
        try:
            instance = ProfileChatSettings.objects.get(
                profile_chat_settings_id=profile_chat_settings_id,
                profile_chat_settings_is_deleted=False
            )
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Profile chat settings not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Handle multipart form data for file upload
            data = request.data.copy()
            
            # If file is uploaded via multipart form
            if 'profile_picture' in request.FILES:
                data['profile_picture'] = request.FILES['profile_picture']
            elif 'profile_picture' in data and data['profile_picture'] == 'null':
                # Handle null value for removing profile picture
                data['profile_picture'] = None
            
            serializer = ProfileChatSettingsSerializer(
                instance, 
                data=data, 
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                
                # Get updated data with working hours
                updated_instance = ProfileChatSettings.objects.get(
                    profile_chat_settings_id=profile_chat_settings_id
                )
                response_serializer = ProfileChatSettingsResponseSerializer(
                    updated_instance, 
                    context={'request': request}
                )
                
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Profile chat settings updated successfully",
                    "data": response_serializer.data
                }, status=status.HTTP_200_OK)
            
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