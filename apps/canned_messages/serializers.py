from rest_framework import serializers
from apps.canned_messages.models import CannedMessage
from django.db import transaction


class CannedMessageSerializer(serializers.Serializer):
    canned_messages_id = serializers.IntegerField(read_only=True)
    canned_messages_name = serializers.CharField(
        max_length=255,
        min_length=3,
        required=True,
        error_messages={
            'required': 'Message Name is required.',
            'blank': 'Message Name cannot be empty.',
            'max_length': 'Message Name cannot exceed 255 characters.',
            'min_length': 'Message Name must be at least 3 characters.'
        }
    )
    canned_messages_type = serializers.ChoiceField(
        choices=[('text', 'Text')],
        default='text',
        error_messages={
            'invalid_choice': 'Type must be valid choices [ text ].'
        }
    )
    canned_messages_description = serializers.CharField(
        required=True,
        min_length=3,
        error_messages={
            'required': 'Description is required.',
            'blank': 'Description cannot be empty.',
            'min_length': 'Message Name must be at least 3 characters.'
        }
    )
    canned_messages_is_favourite = serializers.BooleanField(read_only=True)
    canned_messages_created_by = serializers.CharField(read_only=True)
    canned_messages_updated_by = serializers.CharField(read_only=True)
    canned_messages_is_deleted = serializers.BooleanField(read_only=True)
    canned_messages_created_at = serializers.DateTimeField(read_only=True)
    canned_messages_updated_at = serializers.DateTimeField(read_only=True)

    def validate_canned_messages_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Message Name must be at least 3 characters.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Message Name cannot exceed 255 characters.")
        
        instance = getattr(self, 'instance', None)
        
        queryset = CannedMessage.objects.filter(
            canned_messages_name__iexact=value.strip(),
            canned_messages_is_deleted=False
        )
        
        if instance:
            queryset = queryset.exclude(canned_messages_id=instance.canned_messages_id)
        
        if queryset.exists():
            raise serializers.ValidationError(f"Canned Message with this name '{value}' already exists.")
        
        return value.strip()
    
    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get("request")
        message = CannedMessage.objects.create(
            canned_messages_name=validated_data.get('canned_messages_name'),
            canned_messages_type=validated_data.get('canned_messages_type', 'text'),
            canned_messages_description=validated_data.get('canned_messages_description'),
            canned_messages_created_by=None,
        )
        return message

    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.canned_messages_name = validated_data.get("canned_messages_name", instance.canned_messages_name)
        instance.canned_messages_type = validated_data.get("canned_messages_type", instance.canned_messages_type)
        instance.canned_messages_description = validated_data.get("canned_messages_description", instance.canned_messages_description)
        instance.canned_messages_updated_by = None
        instance.save()
        return instance


class CannedMessageFavouriteSerializer(serializers.Serializer):
    canned_messages_is_favourite = serializers.BooleanField(
        required=True,
        error_messages={
            'required': 'Favourite status is required.',
            'invalid': 'Favourite status must be true or false.'
        }
    )
    
    @transaction.atomic
    def update(self, instance, validated_data):
        instance.canned_messages_is_favourite = validated_data.get("canned_messages_is_favourite")
        instance.canned_messages_updated_by = None
        instance.save()
        return instance