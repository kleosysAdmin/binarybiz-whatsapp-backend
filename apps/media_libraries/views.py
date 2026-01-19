from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from apps.media_libraries.models import MediaLibrary
from apps.media_libraries.serializers import MediaLibrarySerializer
from django.utils.dateparse import parse_date


class MediaLibraryListCreateView(APIView):
    # GET requests to fetch all non-deleted media with filters
    @transaction.atomic
    def get(self, request):
        try:
            media = MediaLibrary.objects.filter(media_libraries_is_deleted=False)
            
            # Filter by media type
            media_type = request.GET.get('media_type')
            if media_type:
                media = media.filter(media_libraries_type=media_type)
            
            # Filter by date
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
                                media = media.filter(
                                    media_libraries_created_at__date__gte=start_date,
                                    media_libraries_created_at__date__lte=end_date
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
                            media = media.filter(media_libraries_created_at__date=filter_date)
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
            
            serializer = MediaLibrarySerializer(media, many=True)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched all media data successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST requests to create new media (upload file)
    @transaction.atomic
    def post(self, request):
        try:
            serializer = MediaLibrarySerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 201,
                    "message": "Media uploaded successfully",
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


class MediaLibraryDetailView(APIView):
    # Retrieve media by ID if not soft deleted
    @transaction.atomic
    def get(self, request, media_libraries_id):
        try:
            media = MediaLibrary.objects.get(media_libraries_id=media_libraries_id, media_libraries_is_deleted=False)
            serializer = MediaLibrarySerializer(media)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched Media by ID Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Media not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update the media (replace file)
    @transaction.atomic
    def put(self, request, media_libraries_id):
        try:
            media = MediaLibrary.objects.get(media_libraries_id=media_libraries_id, media_libraries_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Media not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = MediaLibrarySerializer(media, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Media updated successfully",
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

    # Mark the media as soft deleted and delete file
    @transaction.atomic
    def delete(self, request, media_libraries_id):
        try:
            media = MediaLibrary.objects.get(media_libraries_id=media_libraries_id, media_libraries_is_deleted=False)
            
            # Delete physical file
            if media.media_libraries_file_path:
                try:
                    default_storage.delete(media.media_libraries_file_path)
                except:
                    pass
            
            # Soft delete record
            media.media_libraries_is_deleted = True
            media.save()

            return Response({
                "success": True,
                "status": 200,
                "message": "Media deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Media not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)