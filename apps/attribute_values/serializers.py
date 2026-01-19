from rest_framework import serializers
from apps.attribute_values.models import AttributeValue
from apps.attributes.models import Attribute
from apps.audiences.models import Audience
from django.db import transaction


# Serializer for AttributeValue model, handling creation and updates.
class AttributeValueSerializer(serializers.Serializer):
    attribute_values_id = serializers.IntegerField(read_only=True)
    attribute_values_attributes_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.filter(attributes_is_deleted=False),
        required=True,
        error_messages={
            'required': 'Attribute ID is required.',
            'does_not_exist': 'Attribute does not exist.'
        }
    )
    attribute_values_audiences_id = serializers.PrimaryKeyRelatedField(
        queryset=Audience.objects.filter(audiences_is_deleted=False),
        required=True,
        error_messages={
            'required': 'Audience ID is required.',
            'does_not_exist': 'Audience does not exist.'
        }
    )
    attribute_values_value = serializers.CharField(
        max_length=255,
        min_length=3,
        required=True,
        error_messages={
            'required': 'Attribute value is required.',
            'blank': 'Attribute value cannot be empty.',
            'max_length': 'Attribute value cannot exceed 255 characters.',
            'min_length': 'Attribute value must be atleast 3 characters.',
        }
    )
    attribute_values_created_by = serializers.CharField(read_only=True)
    attribute_values_updated_by = serializers.CharField(read_only=True)
    attribute_values_is_deleted = serializers.BooleanField(read_only=True)
    attribute_values_created_at = serializers.DateTimeField(read_only=True)
    attribute_values_updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        # Check if combination already exists
        instance = getattr(self, 'instance', None)
        attribute = data.get('attribute_values_attributes_id')
        audience = data.get('attribute_values_audiences_id')
        
        if attribute and audience:
            queryset = AttributeValue.objects.filter(
                attribute_values_attributes_id=attribute,
                attribute_values_audiences_id=audience,
                attribute_values_is_deleted=False
            )
            
            if instance:
                queryset = queryset.exclude(attribute_values_id=instance.attribute_values_id)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    f"Attribute value for this attribute and audience combination already exists."
                )
        
        return data
    
    # Creates a new attribute value instance
    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get("request")
        attribute_value = AttributeValue.objects.create(
            attribute_values_attributes_id=validated_data.get('attribute_values_attributes_id'),
            attribute_values_audiences_id=validated_data.get('attribute_values_audiences_id'),
            attribute_values_value=validated_data.get('attribute_values_value'),
            attribute_values_created_by=None,
        )
        return attribute_value

    # Updates an existing attribute value instance
    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.attribute_values_attributes_id = validated_data.get(
            "attribute_values_attributes_id", 
            instance.attribute_values_attributes_id
        )
        instance.attribute_values_audiences_id = validated_data.get(
            "attribute_values_audiences_id", 
            instance.attribute_values_audiences_id
        )
        instance.attribute_values_value = validated_data.get(
            "attribute_values_value", 
            instance.attribute_values_value
        )
        instance.attribute_values_updated_by = None
        instance.save()
        return instance