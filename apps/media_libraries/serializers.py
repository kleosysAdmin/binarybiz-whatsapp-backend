from rest_framework import serializers
from apps.media_libraries.models import MediaLibrary
from django.db import transaction
from django.core.files.storage import default_storage
import os

class MediaLibrarySerializer(serializers.Serializer):
    media_libraries_id = serializers.IntegerField(read_only=True)
    media_file = serializers.FileField(
        write_only=True,
        required=True,
        error_messages={
            'required': 'Media file is required.',
        }
    )
    media_libraries_file_path = serializers.CharField(read_only=True)
    media_libraries_file_size = serializers.IntegerField(read_only=True)  # Raw size in bytes
    media_libraries_file_size_human = serializers.SerializerMethodField(read_only=True)  # Human readable
    media_libraries_type = serializers.CharField(read_only=True)
    media_libraries_is_deleted = serializers.BooleanField(read_only=True)
    media_libraries_created_at = serializers.DateTimeField(read_only=True)
    media_libraries_updated_at = serializers.DateTimeField(read_only=True)

    def get_media_libraries_file_size_human(self, obj):
        """Convert bytes to human readable format"""
        if not obj.media_libraries_file_size:
            return "0 B"
        
        size_bytes = obj.media_libraries_file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} EB"

    def validate_media_file(self, value):
        # File type validation only (no size limit)
        allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma'],
            'file': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', 
                     '.zip', '.rar', '.7z', '.csv', '.xml', '.json', '.rtf']
        }
        
        file_name = value.name.lower()
        file_extension = os.path.splitext(file_name)[1]
        
        # Determine media type
        media_type = None
        for type_name, extensions in allowed_extensions.items():
            if file_extension in extensions:
                media_type = type_name
                break
        
        if not media_type:
            raise serializers.ValidationError(f"Unsupported file type. Allowed: {', '.join(['Images: .jpg, .png', 'Videos: .mp4, .mov', 'Audio: .mp3, .wav', 'Files: .pdf, .docx'])}")
        
        # Add media type to validated data
        self.context['media_type'] = media_type
        return value

    @transaction.atomic()
    def create(self, validated_data):
        media_file = validated_data.pop('media_file')
        media_type = self.context.get('media_type', 'file')
        
        # Generate unique file name
        original_name = media_file.name
        base_name, extension = os.path.splitext(original_name)
        safe_base_name = ''.join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_base_name = safe_base_name.replace(' ', '_')
        unique_name = f"{safe_base_name}_{os.urandom(4).hex()}{extension}"
        
        # Save file to media directory
        file_path = default_storage.save(f'media_library/{unique_name}', media_file)
        
        # Create media library record with BigIntegerField
        media = MediaLibrary.objects.create(
            media_libraries_file_path=file_path,
            media_libraries_file_size=media_file.size,  # This will be stored as BIGINT
            media_libraries_type=media_type,
        )
        
        return media

    @transaction.atomic()
    def update(self, instance, validated_data):
        # For update, we might want to replace the file
        if 'media_file' in validated_data:
            # Delete old file
            if instance.media_libraries_file_path:
                try:
                    default_storage.delete(instance.media_libraries_file_path)
                except:
                    pass
            
            # Save new file
            media_file = validated_data.pop('media_file')
            media_type = self.context.get('media_type', instance.media_libraries_type)
            
            original_name = media_file.name
            base_name, extension = os.path.splitext(original_name)
            safe_base_name = ''.join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_base_name = safe_base_name.replace(' ', '_')
            unique_name = f"{safe_base_name}_{os.urandom(4).hex()}{extension}"
            
            file_path = default_storage.save(f'media_library/{unique_name}', media_file)
            
            instance.media_libraries_file_path = file_path
            instance.media_libraries_file_size = media_file.size  # Stored as BIGINT
            instance.media_libraries_type = media_type
        
        instance.save()
        return instance