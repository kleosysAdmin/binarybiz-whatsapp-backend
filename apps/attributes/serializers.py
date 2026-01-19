from rest_framework import serializers
from apps.attributes.models import Attribute
from django.db import transaction


# Serializer for Attribute model, handling creation and updates.
class AttributeSerializer(serializers.Serializer):
    attributes_id = serializers.IntegerField(read_only=True)
    attributes_name = serializers.CharField(
        max_length=255,
        min_length=3,
        required=True,
        error_messages={
            'required': 'Attribute Name is required.',
            'blank': 'Attribute Name cannot be empty.',
            'max_length': 'Attribute Name cannot exceed 255 characters.',
            'min_length': 'Attribute Name must be atleast 3 characters.'
        }
    )
    attributes_created_by = serializers.CharField(read_only=True)
    attributes_updated_by = serializers.CharField(read_only=True)
    attributes_is_active = serializers.BooleanField(default=True)
    attributes_is_deleted = serializers.BooleanField(read_only=True)
    attributes_created_at = serializers.DateTimeField(read_only=True)
    attributes_updated_at = serializers.DateTimeField(read_only=True)

    def validate_attributes_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Attribute Name must be at least 2 characters.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Attribute Name cannot exceed 255 characters.")
        
        instance = getattr(self, 'instance', None)
        
        queryset = Attribute.objects.filter(
            attributes_name__iexact=value.strip(),
            attributes_is_deleted=False
        )
        
        if instance:
            queryset = queryset.exclude(attributes_id=instance.attributes_id)
        
        if queryset.exists():
            raise serializers.ValidationError(f"Attribute with this name '{value}' already exists.")
        
        return value.strip()
    
    # Creates a new attribute instance
    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get("request")
        attribute = Attribute.objects.create(
            attributes_name=validated_data.get('attributes_name'),
            attributes_created_by=None,
        )
        return attribute

    # Updates an existing attribute instance
    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.attributes_name = validated_data.get("attributes_name", instance.attributes_name)
        instance.attributes_is_active = validated_data.get("attributes_is_active", instance.attributes_is_active)
        instance.attributes_updated_by = None
        instance.save()
        return instance