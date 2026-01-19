from rest_framework import serializers
from apps.labels.models import Label
from django.db import transaction


# Serializer for Label  model, handling creation and updates.
class LabelSerializer(serializers.Serializer):
    labels_id = serializers.IntegerField(read_only=True)
    labels_name = serializers.CharField(
        max_length=255,
        min_length=3,
        required=True,
        error_messages={
            'required': 'Label Name is required.',
            'blank': 'Label Name cannot be empty.',
            'max_length': 'Label Name cannot exceed 255 characters.',
            'min_length': 'Label Name must be atleast 3 characters.'
        })
    labels_description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    labels_created_by = serializers.CharField(read_only=True)
    labels_updated_by = serializers.CharField(read_only=True)
    labels_is_active = serializers.BooleanField(default=True)
    labels_is_deleted = serializers.BooleanField(read_only=True)
    labels_created_at = serializers.DateTimeField(read_only=True)
    labels_updated_at = serializers.DateTimeField(read_only=True)

    def validate_labels_name(self, value):
        
        if len(value) < 2:
            raise serializers.ValidationError("Label Name must be at least 2 characters.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Label Name cannot exceed 255 characters.")
        
        instance = getattr(self, 'instance', None)
        
        queryset = Label.objects.filter(
            labels_name__iexact=value.strip(),
            labels_is_deleted=False
        )
        
        if instance:
            queryset = queryset.exclude(labels_id=instance.labels_id)
        
        if queryset.exists():
            raise serializers.ValidationError(f"label with this name {value} already exists.")
        
        return value.strip()
        
    
    # Creates a new label instance and created by.
    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get("request")
        label =  Label.objects.create(
            labels_name = validated_data.get('labels_name'),
            labels_description = validated_data.get('labels_description'),
            labels_created_by = None,
        )

        return label

    # Updates an existing label instance and update by.
    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.labels_name = validated_data.get("labels_name", instance.labels_name)
        instance.labels_description = validated_data.get("labels_description", instance.labels_description)
        instance.labels_is_active = validated_data.get("labels_is_active", instance.labels_is_active)
        instance.labels_updated_by = None
        instance.save()
        return instance
