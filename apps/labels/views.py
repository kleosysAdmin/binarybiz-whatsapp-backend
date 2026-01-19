from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from apps.labels.models import Label
from apps.audiences.models import Audience
from apps.labels.serializers import LabelSerializer
from django.utils.dateparse import parse_date
from apps.role_permissions_management.permissions.decorators import feature_permission_required




class LabelListCreateView(APIView):

    # GET requests to fetch all non-deleted labels records
    @feature_permission_required(feature_key='label', action_key='read')
    def get(self, request):
        try:
            labels = Label.objects.filter(labels_is_deleted=False)
                
            status_filter = request.GET.get('label_status')
            if status_filter is not None:
                if status_filter.lower() == 'true':
                    labels = labels.filter(labels_is_active=True)
                elif status_filter.lower() == 'false':
                    labels = labels.filter(labels_is_active=False)


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
                                labels = labels.filter(
                                    labels_created_at__date__gte=start_date,
                                    labels_created_at__date__lte=end_date
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
                            labels = labels.filter(labels_created_at__date=filter_date)
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


            serializer = LabelSerializer(labels, many=True)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched all label data successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST requests to create a new label
    @feature_permission_required(feature_key='label', action_key='create')
    @transaction.atomic
    def post(self, request):
        try:
            serializer = LabelSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 201,
                    "message": "Label created successfully",
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


class LabelDetailView(APIView):

    # Retrieve label by ID if not soft deleted
    @feature_permission_required(feature_key='label', action_key='read')
    def get(self, request, labels_id):
        try:
            label = Label.objects.get(labels_id=labels_id, labels_is_deleted=False)
            serializer = LabelSerializer(label)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched Label by ID Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Label not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # update the Label
    @feature_permission_required(feature_key='label', action_key='update')
    @transaction.atomic
    def put(self, request, labels_id):
        try:
            label = Label.objects.get(labels_id=labels_id, labels_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Label not found"
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            serializer = LabelSerializer(label, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Label updated successfully",
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

    # Mark the Label as soft deleted
    @feature_permission_required(feature_key='label', action_key='delete')
    @transaction.atomic
    def delete(self, request, labels_id):
        try:
            label = Label.objects.get(labels_id=labels_id, labels_is_deleted=False)
            label.labels_is_deleted = True
            label.save()

            # Get all audiences that have this label
            audiences_with_label = Audience.objects.filter(
                audiences_labels__contains=[labels_id],
                audiences_is_deleted=False
            )
            
            # Remove this label from all audiences
            for audience in audiences_with_label:
                if label.labels_id in audience.audiences_labels:
                    audience.audiences_labels = [
                        lbl for lbl in audience.audiences_labels 
                        if lbl != label.labels_id
                    ]
                    audience.save(update_fields=['audiences_labels', 'audiences_updated_at'])

            return Response({
                "success": True,
                "status": 200,
                "message": "Label deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Label not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)