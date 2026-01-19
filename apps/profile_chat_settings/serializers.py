from rest_framework import serializers
from apps.profile_chat_settings.models import ProfileChatSettings, WorkingHours, VERTICAL_CHOICES, DAY_CHOICES
from django.db import transaction
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
import os


class WorkingHoursSerializer(serializers.Serializer):
    working_hours_id = serializers.IntegerField(read_only=True)
    working_hours_day = serializers.ChoiceField(
        choices=[choice[0] for choice in DAY_CHOICES],
        required=True,
        error_messages={
            'required': 'Day is required.',
            'invalid_choice': f"Day must be one of: {', '.join([choice[0] for choice in DAY_CHOICES])}."
        }
    )
    working_hours_enabled = serializers.BooleanField(
        default=True,
        required=False
    )
    working_hours_start = serializers.TimeField(
        format='%H:%M',
        input_formats=['%H:%M'],
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'Start time must be in HH:MM format (e.g., 09:00).'
        }
    )
    working_hours_end = serializers.TimeField(
        format='%H:%M', 
        input_formats=['%H:%M'],
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'End time must be in HH:MM format (e.g., 17:00).'
        }
    )

    def validate(self, data):
        start_time = data.get('working_hours_start')
        end_time = data.get('working_hours_end')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'working_hours_end': 'End time must be after start time.'
            })
        
        return data


class ProfileChatSettingsSerializer(serializers.Serializer):
    profile_chat_settings_id = serializers.IntegerField(read_only=True)
    
    # Profile Picture File Upload (write-only)
    profile_picture = serializers.FileField(
        write_only=True,
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'Please upload a valid image file.'
        }
    )
    
    # Profile Picture Path (read-only after upload)
    profile_chat_settings_profile_picture_path = serializers.CharField(read_only=True)
    
    # Profile Picture URL (read-only)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    
    # Description
    profile_chat_settings_description = serializers.CharField(
        max_length=256,
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'max_length': 'Description cannot exceed 256 characters.'
        }
    )
    
    # Address
    profile_chat_settings_address = serializers.CharField(
        max_length=256,
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'max_length': 'Address cannot exceed 256 characters.'
        }
    )
    
    # Email
    profile_chat_settings_email = serializers.EmailField(
        max_length=256,
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'max_length': 'Email cannot exceed 256 characters.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    # Vertical
    profile_chat_settings_vertical = serializers.ChoiceField(
        choices=[choice[0] for choice in VERTICAL_CHOICES],
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid_choice': f"Vertical must be one of: {', '.join([choice[0] for choice in VERTICAL_CHOICES])}."
        }
    )
    
    # Websites (list of URLs)
    profile_chat_settings_websites = serializers.ListField(
        child=serializers.CharField(max_length=256),
        max_length=2,
        required=False,
        allow_empty=True,
        allow_null=True,
        error_messages={
            'max_length': 'Maximum 2 websites allowed.',
            'not_a_list': 'Websites must be a list of URLs.'
        }
    )
    
    # Auto Resolve
    profile_chat_settings_auto_resolve = serializers.BooleanField(
        default=True,
        required=False
    )
    
    # Welcome Message
    profile_chat_settings_welcome_message = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'required': 'Welcome message is required.'
        }
    )
    
    # Off Hours Message
    profile_chat_settings_off_hours_message = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'required': 'Off hours message is required.'
        }
    )
    
    # Timezone
    profile_chat_settings_timezone = serializers.CharField(
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'max_length': 'Timezone cannot exceed 255 characters.'
        }
    )
    
    # Working hours field (using profile_chat_settings_working_hours as field name)
    profile_chat_settings_working_hours = WorkingHoursSerializer(
        many=True,
        required=False,
        allow_null=True
    )
    
    # Read-only fields
    profile_chat_settings_created_by = serializers.CharField(read_only=True)
    profile_chat_settings_updated_by = serializers.CharField(read_only=True)
    profile_chat_settings_is_deleted = serializers.BooleanField(read_only=True)
    profile_chat_settings_created_at = serializers.DateTimeField(read_only=True)
    profile_chat_settings_updated_at = serializers.DateTimeField(read_only=True)

    def get_profile_picture_url(self, obj):
        if not obj.profile_chat_settings_profile_picture_path:
            return None
        
        return settings.MEDIA_URL + obj.profile_chat_settings_profile_picture_path

    def validate_profile_picture(self, value):
        if value is None:
            return value
        
        # File size validation
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Profile picture size cannot exceed 5MB. Current size: {value.size / 1024 / 1024:.2f}MB"
            )
        
        # File type validation (images only)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_name = value.name.lower()
        file_extension = os.path.splitext(file_name)[1]
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value

    def validate_profile_chat_settings_websites(self, value):
        if value is None:
            return []
        
        if len(value) > 2:
            raise serializers.ValidationError("Maximum 2 websites allowed.")
        
        validator = URLValidator()
        validated_urls = []
        
        for url in value:
            if url:
                if not url.startswith(('http://', 'https://', 'file://')):
                    raise serializers.ValidationError(
                        f"URL '{url}' must start with http://, https://, or file://"
                    )
                
                if not url.startswith('file://'):
                    try:
                        validator(url)
                    except ValidationError:
                        raise serializers.ValidationError(f"'{url}' is not a valid URL.")
                
                if len(url) > 256:
                    raise serializers.ValidationError(f"URL '{url}' exceeds 256 characters.")
                
                validated_urls.append(url)
        
        return validated_urls

    def save_profile_picture(self, instance, profile_picture):
        if profile_picture is None:
            return
        
        if instance.profile_chat_settings_profile_picture_path:
            try:
                default_storage.delete(instance.profile_chat_settings_profile_picture_path)
            except:
                pass
        
        original_name = profile_picture.name
        base_name, extension = os.path.splitext(original_name)
        safe_base_name = ''.join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_base_name = safe_base_name.replace(' ', '_')
        unique_name = f"{safe_base_name}_{os.urandom(4).hex()}{extension}"
        
        # Save file to media directory
        file_path = default_storage.save(f'profile_pictures/{unique_name}', profile_picture)
        
        # Update instance with file path
        instance.profile_chat_settings_profile_picture_path = file_path

    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get("request")
        
        profile_picture = validated_data.pop('profile_picture', None)
        working_hours_data = validated_data.pop('profile_chat_settings_working_hours', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if profile_picture is not None:
            self.save_profile_picture(instance, profile_picture)
        elif 'profile_picture' in self.initial_data and self.initial_data['profile_picture'] is None:
            if instance.profile_chat_settings_profile_picture_path:
                try:
                    default_storage.delete(instance.profile_chat_settings_profile_picture_path)
                except:
                    pass
            instance.profile_chat_settings_profile_picture_path = None
        
        instance.profile_chat_settings_updated_by = None
        instance.save()
        if working_hours_data:
            for hour_data in working_hours_data:
                day = hour_data.get('working_hours_day')
                
                WorkingHours.objects.update_or_create(
                    working_hours_profile_chat_settings_id=instance,
                    working_hours_day=day,
                    defaults={
                        'working_hours_enabled': hour_data.get('working_hours_enabled', True),
                        'working_hours_start': hour_data.get('working_hours_start'),
                        'working_hours_end': hour_data.get('working_hours_end'),
                    }
                )
        
        return instance


class ProfileChatSettingsResponseSerializer(serializers.Serializer):
    profile_chat_settings_id = serializers.IntegerField()
    profile_chat_settings_profile_picture_path = serializers.CharField()
    profile_picture_url = serializers.SerializerMethodField()
    profile_chat_settings_description = serializers.CharField()
    profile_chat_settings_address = serializers.CharField()
    profile_chat_settings_email = serializers.CharField()
    profile_chat_settings_vertical = serializers.CharField()
    profile_chat_settings_websites = serializers.ListField()
    profile_chat_settings_auto_resolve = serializers.BooleanField()
    profile_chat_settings_welcome_message = serializers.CharField()
    profile_chat_settings_off_hours_message = serializers.CharField()
    profile_chat_settings_timezone = serializers.CharField()
    profile_chat_settings_working_hours = serializers.SerializerMethodField()
    
    def get_profile_picture_url(self, obj):
        if not obj.profile_chat_settings_profile_picture_path:
            return None
        
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                settings.MEDIA_URL + obj.profile_chat_settings_profile_picture_path
            )
        
        return settings.MEDIA_URL + obj.profile_chat_settings_profile_picture_path
    
    def get_profile_chat_settings_working_hours(self, obj):
        hours = WorkingHours.objects.filter(
            working_hours_profile_chat_settings_id=obj
        ).order_by('working_hours_id')
        
        return WorkingHoursSerializer(hours, many=True).data