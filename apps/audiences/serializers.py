from rest_framework import serializers
from apps.audiences.models import Audience
from django.db import transaction
import re
from django.utils import timezone
from apps.labels.models import Label
from apps.attribute_values.models import AttributeValue


# Serializer for Audience model, handling creation and updates.
class AudienceSerializer(serializers.Serializer):
    audiences_id = serializers.IntegerField(read_only=True)
    audiences_name = serializers.CharField(
        max_length=255, 
        min_length=3,
        required=True,
        error_messages={
            'required': 'Audience Name is required.',
            'blank': 'Audience Name cannot be empty.',
            'max_length': 'Audience Name cannot exceed 255 characters.',
            'min_length': 'Audience Name must be atleast 3 characters.'
        }
    )
    audiences_phone_number = serializers.CharField(
        max_length=20,
        min_length=10,
        required=True,
        error_messages={
            'required': 'Audience Phone Number is required.',
            'blank': 'Audience Phone Number cannot be empty.',
            'max_length': 'Phone number cannot exceed 20 characters.',
            'min_length': 'Phone number atleast 10 characters.'
        }
    )
    audiences_email = serializers.EmailField(
        required=False, 
        allow_null=True, 
        allow_blank=True,
        error_messages={
            'invalid': 'Please enter a valid email address.'
        }
    )
    audiences_source = serializers.ChoiceField(
        choices=[('organic', 'Organic'), ('imported', 'Imported')],
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid_choice': 'Source must be valid choices [ organic, imported ].'
        }
    )
    audiences_opted = serializers.ChoiceField(
        choices=[('in', 'In'), ('out', 'Out')],
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid_choice': 'Opted must be valid choices [ in , out ].'
        }
    )
    audiences_labels = serializers.ListField(
        child=serializers.CharField(), 
        required=False,
        allow_null=True,
        allow_empty=True,
        error_messages={
            'not_a_list': 'Labels must be provided as a list.',
        }
    )
    audiences_last_active = serializers.DateTimeField(read_only=True)
    audiences_created_by = serializers.CharField(read_only=True)
    audiences_updated_by = serializers.CharField(read_only=True)
    audiences_is_active = serializers.BooleanField(default=True)
    audiences_is_deleted = serializers.BooleanField(read_only=True)
    audiences_created_at = serializers.DateTimeField(read_only=True)
    audiences_updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        label_ids = instance.audiences_labels if instance.audiences_labels else []
        
        if label_ids:
            # Convert all label IDs to integers
            label_ids_int = []
            for label_id in label_ids:
                try:
                    label_ids_int.append(int(label_id))
                except (ValueError, TypeError):
                    continue
            
            # Get label names for label IDs
            labels = Label.objects.filter(
                labels_id__in=label_ids_int,
                labels_is_deleted=False
            ).values('labels_id', 'labels_name')
            
            # Create mapping of label_id -> label_name
            label_name_map = {}
            for label in labels:
                label_name_map[str(label['labels_id'])] = label['labels_name']
            
            # Replace label IDs with label names in response
            label_names = []
            for label_id in label_ids:
                label_str = str(label_id)
                if label_str in label_name_map:
                    label_names.append(label_name_map[label_str])
                else:
                    label_names.append(label_str)
            
            representation['audiences_labels'] = label_names
        else:
            representation['audiences_labels'] = []
        
        
        # Get attributes for this audience
        attributes = AttributeValue.objects.filter(
            attribute_values_audiences_id=instance,
            attribute_values_is_deleted=False
        ).select_related('attribute_values_attributes_id')
        
        # Create attributes dictionary with attribute names and values
        attributes_dict = {}
        for attr_value in attributes:
            if attr_value.attribute_values_attributes_id:
                attr_name = attr_value.attribute_values_attributes_id.attributes_name
                attributes_dict[attr_name] = attr_value.attribute_values_value
        
        representation['audiences_attributes'] = attributes_dict
        
        return representation


    def validate_audiences_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Audience Name must be at least 2 characters.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Audience Name cannot exceed 255 characters.")
        
        return value.strip()

    def validate_audiences_phone_number(self, value):
        if value:
            # Remove spaces, dashes, and parentheses
            phone = re.sub(r'[+\s\-()]', '', value)
            if not phone.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")

            # Check length
            if len(value) != 10:
                raise serializers.ValidationError("Phone number must be exactly 10 digits.")

            # Check uniqueness
            instance = getattr(self, 'instance', None)
            queryset = Audience.objects.filter(
                audiences_phone_number=phone,
                audiences_is_deleted=False
            )
            
            if instance:
                queryset = queryset.exclude(audiences_id=instance.audiences_id)
            
            if queryset.exists():
                raise serializers.ValidationError(f"Audience with phone number '{phone}' already exists.")
            
            return phone
        return value

    def validate_audiences_email(self, value):
        if value:
            instance = getattr(self, 'instance', None)
            queryset = Audience.objects.filter(
                audiences_email=value.strip().lower(),
                audiences_is_deleted=False
            )
            
            if instance:
                queryset = queryset.exclude(audiences_id=instance.audiences_id)
            
            if queryset.exists():
                raise serializers.ValidationError(f"Audience with email '{value}' already exists.")
            
            return value.strip().lower()
        return value
    
    def validate_audiences_labels(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise serializers.ValidationError("Labels must be provided as a list.")
            
            # If empty list, return as is
            if not value:
                return []
            
            # Convert string numbers to integers
            label_ids = []
            for i, item in enumerate(value):
                try:
                    # Try to convert to integer (handles both "1" and 1)
                    if isinstance(item, str) and item.isdigit():
                        label_ids.append(int(item))
                    elif isinstance(item, int):
                        label_ids.append(item)
                    else:
                        raise serializers.ValidationError(
                            f"Label at position {i} must be an integer. Received: {repr(item)}"
                        )
                except (ValueError, TypeError) as e:
                    raise serializers.ValidationError(
                        f"Label at position {i} must be an integer. Received: {repr(item)}"
                    )
            
            # Check for duplicates
            if len(label_ids) != len(set(label_ids)):
                raise serializers.ValidationError("Duplicate label IDs are not allowed.")
            
            # Validate against Label model (only if we have labels)
            if label_ids:
                invalid_labels = []
                
                # Get all valid, non-deleted labels
                valid_label_ids = Label.objects.filter(
                    labels_id__in=label_ids,
                    labels_is_deleted=False,
                    labels_is_active=True
                ).values_list('labels_id', flat=True)
                
                valid_label_set = set(valid_label_ids)
                
                for label_id in label_ids:
                    if label_id not in valid_label_set:
                        invalid_labels.append(str(label_id))
                
                if invalid_labels:
                    if len(invalid_labels) == 1:
                        error_msg = f"Label ID {invalid_labels[0]} is invalid or not found."
                    else:
                        error_msg = f"Label IDs {', '.join(invalid_labels)} are invalid or not found."
                    raise serializers.ValidationError(error_msg)
            
            return label_ids
        
        return value

    
    # Creates a new audience instance
    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get("request")
        audience = Audience.objects.create(
            audiences_name=validated_data.get('audiences_name'),
            audiences_phone_number=validated_data.get('audiences_phone_number'),
            audiences_email=validated_data.get('audiences_email'),
            audiences_source=validated_data.get('audiences_source'),
            audiences_opted=validated_data.get('audiences_opted'),
            audiences_labels=validated_data.get('audiences_labels', []),
            audiences_last_active=timezone.now(),
            audiences_created_by=None,
        )
        return audience

    # Updates an existing audience instance
    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.audiences_name = validated_data.get("audiences_name", instance.audiences_name)
        instance.audiences_phone_number = validated_data.get("audiences_phone_number", instance.audiences_phone_number)
        instance.audiences_email = validated_data.get("audiences_email", instance.audiences_email)
        instance.audiences_source = validated_data.get("audiences_source", instance.audiences_source)
        instance.audiences_opted = validated_data.get("audiences_opted", instance.audiences_opted)
        instance.audiences_labels = validated_data.get("audiences_labels", instance.audiences_labels)
        instance.audiences_is_active = validated_data.get("audiences_is_active", instance.audiences_is_active)
        instance.audiences_last_active = timezone.now()
        instance.audiences_updated_by = None
        instance.save()
        return instance

class AudienceStatusSerializer(serializers.Serializer):
    audiences_is_active = serializers.BooleanField(
        required=True,
        error_messages={
            'required': 'audience status is required.',
            'invalid': 'audience status must be true or false.'
        }
    )
    
    def update(self, instance, validated_data):
        instance.audiences_is_active = validated_data.get("audiences_is_active")
        instance.audiences_updated_by = None
        instance.save()
        return instance


class AudienceImportSerializer(serializers.Serializer):
    audiences_name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Audience Name is required.',
            'blank': 'Audience Name cannot be empty.'
        }
    )
    audiences_phone_number = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': 'Audience Phone Number is required.',
            'blank': 'Audience Phone Number cannot be empty.'
        }
    )
    audiences_email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid': 'Please enter a valid email address.'
        }
    )
    audiences_source = serializers.ChoiceField(
        choices=[('organic', 'Organic'), ('imported', 'Imported')],
        required=False,
        allow_null=True,
        allow_blank=True,
        default='imported'
    )
    audiences_opted = serializers.ChoiceField(
        choices=[('in', 'In'), ('out', 'Out')],
        required=False,
        allow_null=True,
        allow_blank=True,
        default='in'
    )
    audiences_labels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        default=[]
    )
    audiences_attributes = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        default={}
    )
    audiences_is_active = serializers.BooleanField(default=True)

    def validate_audiences_phone_number(self, value):
        if value:
            # Remove spaces, dashes, and parentheses
            phone = re.sub(r'[+\s\-()]', '', value)
            if not phone.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
            
            if len(phone) != 10:
                raise serializers.ValidationError("Phone number must be exactly 10 digits.")
            
            return phone
        return value

    def validate_audiences_email(self, value):
        if value:
            return value.strip().lower()
        return value

    def validate_audiences_labels(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Labels must be provided as a list.")
        return value

    def validate_audiences_attributes(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Attributes must be provided as a dictionary.")
        return value