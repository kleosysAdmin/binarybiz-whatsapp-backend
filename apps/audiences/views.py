from rest_framework.views import APIView
from django.db import transaction ,IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from apps.audiences.models import Audience
from apps.audiences.serializers import AudienceSerializer , AudienceImportSerializer, AudienceStatusSerializer
import json
import re

from django.utils.dateparse import  parse_datetime
from django.utils import timezone
from apps.attribute_values.models import AttributeValue


from apps.labels.models import Label
from apps.attributes.models import Attribute

from django.utils.dateparse import parse_date


class AudienceListCreateView(APIView):
    # GET requests to fetch audiences with filters
    @transaction.atomic
    def get(self, request):
        try:
            audiences = Audience.objects.filter(audiences_is_deleted=False)
            
            # Filter by Audience Status
            status_filter = request.GET.get('audiences_status')
            if status_filter is not None:
                if status_filter.lower() == 'true':
                    audiences = audiences.filter(audiences_is_active=True)
                elif status_filter.lower() == 'false':
                    audiences = audiences.filter(audiences_is_active=False)
            
            # Filter by Source
            source_filter = request.GET.get('audiences_source')
            if source_filter:
                audiences = audiences.filter(audiences_source=source_filter)
            
            # Filter by Opted
            opted_filter = request.GET.get('audiences_opted')
            if opted_filter:
                audiences = audiences.filter(audiences_opted=opted_filter)
            
            # Filter by Label (by label name)
            label_filter = request.GET.get('audiences_label')
            if label_filter:
                try:
                    # Get label ID from name
                    label = Label.objects.get(
                        labels_name__iexact=label_filter.strip(),
                        labels_is_deleted=False,
                        labels_is_active=True
                    )
                    # Filter audiences that have this label ID in their labels array
                    audiences = audiences.filter(audiences_labels__contains=[label.labels_id])
                except Label.DoesNotExist:
                    return Response({
                        "success": False,
                        "status": 400,
                        "message": f"Label '{label_filter}' not found",
                        "error": "Invalid label name"
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
                                audiences = audiences.filter(
                                    audiences_created_at__date__gte=start_date,
                                    audiences_created_at__date__lte=end_date
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
                            audiences = audiences.filter(audiences_created_at__date=filter_date)
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
            
            # Date filtering for last_active
            last_active_param = request.GET.get('last_active')
            if last_active_param:
                try:
                    if 'to' in last_active_param.lower():
                        date_parts = last_active_param.lower().split('to')
                        if len(date_parts) == 2:
                            start_date_str = date_parts[0].strip()
                            end_date_str = date_parts[1].strip()
                            
                            start_date = parse_date(start_date_str)
                            end_date = parse_date(end_date_str)
                            
                            if start_date and end_date:
                                audiences = audiences.filter(
                                    audiences_last_active__date__gte=start_date,
                                    audiences_last_active__date__lte=end_date
                                )
                            else:
                                return Response({
                                    "success": False,
                                    "status": 400,
                                    "message": "Invalid date range format for last_active. Use 'YYYY-MM-DD to YYYY-MM-DD' with valid dates",
                                    "error": "Invalid date format in range"
                                }, status=status.HTTP_400_BAD_REQUEST)
                    
                    elif '-' in last_active_param and last_active_param.count('-') >= 2:
                        filter_date = parse_date(last_active_param)
                        if filter_date:
                            audiences = audiences.filter(audiences_last_active__date=filter_date)
                        else:
                            return Response({
                                "success": False,
                                "status": 400,
                                "message": "Invalid date format for last_active. Use 'YYYY-MM-DD'",
                                "error": "Invalid date format"
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        return Response({
                            "success": False,
                            "status": 400,
                            "message": "Invalid last_active parameter. Use 'YYYY-MM-DD' for single date or 'YYYY-MM-DD to YYYY-MM-DD' for range",
                            "error": "Invalid date parameter format"
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except ValueError as e:
                    return Response({
                        "success": False,
                        "status": 400,
                        "message": "Invalid date value for last_active",
                        "error": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({
                        "success": False,
                        "status": 400,
                        "message": "Error processing last_active filter",
                        "error": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            
            serializer = AudienceSerializer(audiences, many=True)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched audience data successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST requests to create a new audience
    @transaction.atomic
    def post(self, request):
        try:
            serializer = AudienceSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 201,
                    "message": "Audience created successfully",
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


class AudienceDetailView(APIView):
    # Retrieve audience by ID if not soft deleted
    @transaction.atomic
    def get(self, request, audiences_id):
        try:
            audience = Audience.objects.get(audiences_id=audiences_id, audiences_is_deleted=False)
            serializer = AudienceSerializer(audience)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched Audience by ID Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Audience not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update the audience
    @transaction.atomic
    def put(self, request, audiences_id):
        try:
            audience = Audience.objects.get(audiences_id=audiences_id, audiences_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Audience not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = AudienceSerializer(audience, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Audience updated successfully",
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

    # Mark the audience as soft deleted
    @transaction.atomic
    def delete(self, request, audiences_id):
        try:
            audience = Audience.objects.get(audiences_id=audiences_id, audiences_is_deleted=False)
            audience.audiences_is_deleted = True
            audience.save()

            # Soft-deletes related Attribute Values objects.
            AttributeValue.objects.filter(
                attribute_values_audiences_id=audience,
                attribute_values_is_deleted=False
            ).update(attribute_values_is_deleted=True)

            return Response({
                "success": True,
                "status": 200,
                "message": "Audience deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Audience not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AudienceStatusDetailView(APIView):
    
    # Update the audience
    @transaction.atomic
    def put(self, request, audiences_id):
        try:
            audience = Audience.objects.get(audiences_id=audiences_id, audiences_is_deleted=False)
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Audience not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = AudienceStatusSerializer(audience, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Audience Status updated successfully",
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



# Import audiences with optional skip functionality
class AudienceImportView(APIView):
    
    @transaction.atomic
    def post(self, request):
        try:
            # parse request data
            skip_existing = request.data.get('skip_existing', True)
            audiences_data = request.data.get('audiences', [])
            
            if not isinstance(audiences_data, list):
                return Response({
                    "success": False,
                    "status": 400,
                    "message": "Invalid Input",
                    "error": "audiences must be a list"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not audiences_data:
                return Response({
                    "success": False,
                    "status": 400,
                    "message": "Invalid Input",
                    "error": "No audience data provided"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            results = {
                "success": True,
                "status": 200,
                "message": "Import completed",
                "summary": {
                    "total": len(audiences_data),
                    "created": 0,
                    "updated": 0,
                    "skipped": 0,
                    "failed": 0
                },
                "details": []
            }
            
            # Pre-fetch existing labels and attributes for performance
            existing_labels_cache = {}
            existing_attributes_cache = {}
            
            # Batch phone numbers to check existing audiences
            phone_numbers = []
            for audience_data in audiences_data:
                phone = audience_data.get('audiences_phone_number')
                if phone:
                    phone = re.sub(r'[+\s\-()]', '', phone)
                    phone_numbers.append(phone)
            
            # Get existing audiences by phone number
            existing_audiences = {}
            if phone_numbers:
                existing_auds = Audience.objects.filter(
                    audiences_phone_number__in=phone_numbers,
                    audiences_is_deleted=False
                )
                for aud in existing_auds:
                    existing_audiences[aud.audiences_phone_number] = aud
            
            # Get all label names to create missing ones
            label_names = set()
            for audience_data in audiences_data:
                labels = audience_data.get('audiences_labels', [])
                for label_name in labels:
                    if isinstance(label_name, str) and label_name.strip():
                        label_names.add(label_name.strip().lower())
            
            # Get or create labels
            if label_names:
                existing_labels = Label.objects.filter(
                    labels_name__in=[name.title() for name in label_names],
                    labels_is_deleted=False
                )
                for label in existing_labels:
                    existing_labels_cache[label.labels_name.lower()] = label.labels_id
                
                # Create missing labels
                existing_label_names = {name.lower() for name in existing_labels_cache.keys()}
                new_labels_to_create = []
                
                for label_name in label_names:
                    if label_name not in existing_label_names:
                        # Create new label
                        label = Label(
                            labels_name=label_name.title(),
                            labels_created_by=None,
                            labels_is_active=True
                        )
                        new_labels_to_create.append(label)
                
                if new_labels_to_create:
                    Label.objects.bulk_create(new_labels_to_create)
                    # Update cache with new labels
                    new_labels = Label.objects.filter(
                        labels_name__in=[l.labels_name for l in new_labels_to_create],
                        labels_is_deleted=False
                    )
                    for label in new_labels:
                        existing_labels_cache[label.labels_name.lower()] = label.labels_id
            
            # Get all attribute names to create missing ones
            attribute_names = set()
            for audience_data in audiences_data:
                attributes = audience_data.get('audiences_attributes', {})
                for attr_name in attributes.keys():
                    if isinstance(attr_name, str) and attr_name.strip():
                        attribute_names.add(attr_name.strip().lower())
            
            # Get or create attributes
            if attribute_names:
                existing_attrs = Attribute.objects.filter(
                    attributes_name__in=[name.title() for name in attribute_names],
                    attributes_is_deleted=False
                )
                for attr in existing_attrs:
                    existing_attributes_cache[attr.attributes_name.lower()] = attr
                
                # Create missing attributes
                existing_attr_names = {name.lower() for name in existing_attributes_cache.keys()}
                new_attrs_to_create = []
                
                for attr_name in attribute_names:
                    if attr_name not in existing_attr_names:
                        # Create new attribute
                        attr = Attribute(
                            attributes_name=attr_name.title(),
                            attributes_created_by=None,
                            attributes_is_active=True
                        )
                        new_attrs_to_create.append(attr)
                
                if new_attrs_to_create:
                    Attribute.objects.bulk_create(new_attrs_to_create)
                    # Update cache with new attributes
                    new_attrs = Attribute.objects.filter(
                        attributes_name__in=[a.attributes_name for a in new_attrs_to_create],
                        attributes_is_deleted=False
                    )
                    for attr in new_attrs:
                        existing_attributes_cache[attr.attributes_name.lower()] = attr
            
            # Process each audience
            audiences_to_create = []
            audiences_to_update = []
            attribute_values_to_create = []
            attribute_values_to_update = []
            
            for index, audience_data in enumerate(audiences_data):
                detail = {
                    "index": index,
                    "phone_number": audience_data.get('audiences_phone_number'),
                    "status": "pending",
                    "message": "",
                    "audience_id": None
                }
                
                try:
                    # Validate the data
                    serializer = AudienceImportSerializer(data=audience_data)
                    if not serializer.is_valid():
                        error_msg = list(serializer.errors.values())[0][0] if serializer.errors else "Invalid data"
                        detail["status"] = "failed"
                        detail["message"] = f"Validation error: {error_msg}"
                        results["summary"]["failed"] += 1
                        results["details"].append(detail)
                        continue
                    
                    validated_data = serializer.validated_data
                    phone_number = validated_data['audiences_phone_number']
                    
                    # Check if audience exists
                    existing_audience = existing_audiences.get(phone_number)
                    
                    if existing_audience and skip_existing:
                        # Skip existing audience
                        detail["status"] = "skipped"
                        detail["message"] = "Audience already exists and skip_existing is true"
                        detail["audience_id"] = existing_audience.audiences_id
                        results["summary"]["skipped"] += 1
                        results["details"].append(detail)
                        continue
                    
                    # Process labels
                    label_ids = []
                    label_names_input = validated_data.get('audiences_labels', [])
                    for label_name in label_names_input:
                        if isinstance(label_name, str) and label_name.strip():
                            label_key = label_name.strip().lower()
                            if label_key in existing_labels_cache:
                                label_ids.append(existing_labels_cache[label_key])
                            else:
                                # Try to find label by name (case-insensitive)
                                try:
                                    label = Label.objects.get(
                                        labels_name__iexact=label_name.strip(),
                                        labels_is_deleted=False,
                                        labels_is_active=True
                                    )
                                    label_ids.append(label.labels_id)
                                    existing_labels_cache[label_key] = label.labels_id
                                except Label.DoesNotExist:
                                    # Skip this label if not found
                                    pass
                    
                    # Process attributes
                    attributes_input = validated_data.get('audiences_attributes', {})
                    
                    if existing_audience:
                        # Update existing audience
                        audience = existing_audience
                        audience.audiences_name = validated_data['audiences_name']
                        audience.audiences_email = validated_data.get('audiences_email', audience.audiences_email)
                        audience.audiences_source = validated_data.get('audiences_source', audience.audiences_source)
                        audience.audiences_opted = validated_data.get('audiences_opted', audience.audiences_opted)
                        
                        # Merge labels (add new ones, keep existing)
                        existing_labels = set(audience.audiences_labels or [])
                        new_labels = set(label_ids)
                        audience.audiences_labels = list(existing_labels.union(new_labels))
                        
                        audience.audiences_is_active = validated_data.get('audiences_is_active', audience.audiences_is_active)
                        audience.audiences_last_active = timezone.now()
                        audience.audiences_updated_by = None
                        
                        audiences_to_update.append(audience)
                        detail["status"] = "updated"
                        detail["audience_id"] = audience.audiences_id
                        results["summary"]["updated"] += 1
                        
                        # Process attributes for update
                        if attributes_input:
                            for attr_name, attr_value in attributes_input.items():
                                attr_key = attr_name.strip().lower()
                                if attr_key in existing_attributes_cache:
                                    attribute = existing_attributes_cache[attr_key]
                                    # Check if attribute value already exists
                                    try:
                                        attr_value_obj = AttributeValue.objects.get(
                                            attribute_values_attributes_id=attribute,
                                            attribute_values_audiences_id=audience,
                                            attribute_values_is_deleted=False
                                        )
                                        # Update existing attribute value
                                        attr_value_obj.attribute_values_value = str(attr_value)
                                        attr_value_obj.attribute_values_updated_by = None
                                        attribute_values_to_update.append(attr_value_obj)
                                    except AttributeValue.DoesNotExist:
                                        # Create new attribute value
                                        attr_value_obj = AttributeValue(
                                            attribute_values_attributes_id=attribute,
                                            attribute_values_audiences_id=audience,
                                            attribute_values_value=str(attr_value),
                                            attribute_values_created_by=None
                                        )
                                        attribute_values_to_create.append(attr_value_obj)
                    
                    else:
                        # Create new audience
                        audience = Audience(
                            audiences_name=validated_data['audiences_name'],
                            audiences_phone_number=phone_number,
                            audiences_email=validated_data.get('audiences_email'),
                            audiences_source=validated_data.get('audiences_source', 'imported'),
                            audiences_opted=validated_data.get('audiences_opted', 'in'),
                            audiences_labels=label_ids,
                            audiences_last_active=timezone.now(),
                            audiences_created_by=None,
                            audiences_is_active=validated_data.get('audiences_is_active', True)
                        )
                        audiences_to_create.append(audience)
                        detail["status"] = "created"
                        results["summary"]["created"] += 1
                
                except Exception as e:
                    detail["status"] = "failed"
                    detail["message"] = str(e)
                    results["summary"]["failed"] += 1
                
                results["details"].append(detail)
            
            # Batch create/update operations
            if audiences_to_create:
                Audience.objects.bulk_create(audiences_to_create)
                # Update detail records with created IDs
                for i, audience in enumerate(audiences_to_create):
                    for detail in results["details"]:
                        if detail["phone_number"] == audience.audiences_phone_number and detail["status"] == "created":
                            detail["audience_id"] = audience.audiences_id
            
            if audiences_to_update:
                Audience.objects.bulk_update(
                    audiences_to_update,
                    [
                        'audiences_name', 'audiences_email', 'audiences_source',
                        'audiences_opted', 'audiences_labels', 'audiences_is_active',
                        'audiences_last_active', 'audiences_updated_by', 'audiences_updated_at'
                    ]
                )
            
            # Process attribute values for created audiences
            if attribute_values_to_create:
                AttributeValue.objects.bulk_create(attribute_values_to_create)
            
            if attribute_values_to_update:
                AttributeValue.objects.bulk_update(
                    attribute_values_to_update,
                    ['attribute_values_value', 'attribute_values_updated_by', 'attribute_values_updated_at']
                )
            
            # Process attributes for newly created audiences
            if audiences_to_create and attributes_input:
                for audience in audiences_to_create:
                    for attr_name, attr_value in attributes_input.items():
                        attr_key = attr_name.strip().lower()
                        if attr_key in existing_attributes_cache:
                            attribute = existing_attributes_cache[attr_key]
                            # Create attribute value for new audience
                            AttributeValue.objects.create(
                                attribute_values_attributes_id=attribute,
                                attribute_values_audiences_id=audience,
                                attribute_values_value=str(attr_value),
                                attribute_values_created_by=None
                            )
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error during import",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)