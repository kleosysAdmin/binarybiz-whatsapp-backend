from rest_framework import serializers
from apps.opt_keywords.models import OptKeyword
from django.db import transaction


class OptKeywordSerializer(serializers.Serializer):
    opt_keywords_id = serializers.IntegerField(read_only=True)
    opt_keywords_type = serializers.ChoiceField(
        choices=[('opt_in', 'Opt-in'), ('opt_out', 'Opt-out')],
        required=True,
        error_messages={
            'required': 'Opt keyword type is required.',
            'invalid_choice': 'Type must be either "opt_in" or "opt_out".'
        }
    )
    opt_keywords_keyword = serializers.ListField(
        child=serializers.CharField(
            max_length=100,
            trim_whitespace=True
        ),
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'Keywords list is required.',
            'empty': 'Keywords list cannot be empty.',
            'not_a_list': 'Keywords must be provided as a list.'
        }
    )
    opt_keywords_automated_response = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=1000,
        error_messages={
            'max_length': 'Automated response cannot exceed 1000 characters.'
        }
    )
    opt_keywords_is_deleted = serializers.BooleanField(read_only=True)
    opt_keywords_created_at = serializers.DateTimeField(read_only=True)
    opt_keywords_updated_at = serializers.DateTimeField(read_only=True)

    def validate_opt_keywords_keyword(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Keywords must be provided as a list.")
        
        if len(value) == 0:
            raise serializers.ValidationError("Keywords list cannot be empty.")
        
        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 keywords allowed per type.")
        
        # Clean and validate each keyword
        cleaned_keywords = []
        seen_keywords = set()
        
        for i, keyword in enumerate(value):
            if not isinstance(keyword, str):
                raise serializers.ValidationError(f"Keyword at position {i+1} must be a string.")
            
            keyword_clean = keyword.strip().lower()
            
            if not keyword_clean:
                raise serializers.ValidationError(f"Keyword at position {i+1} cannot be empty or whitespace.")
            
            if len(keyword_clean) > 100:
                raise serializers.ValidationError(f"Keyword at position {i+1} cannot exceed 100 characters.")
            
            if keyword_clean in seen_keywords:
                raise serializers.ValidationError(f"Duplicate keyword found: '{keyword}'")
            
            seen_keywords.add(keyword_clean)
            cleaned_keywords.append(keyword_clean)
        
        return cleaned_keywords

    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get('request')
        
        # Check if this type already has an active configuration
        existing_config = OptKeyword.objects.filter(
            opt_keywords_type=validated_data['opt_keywords_type'],
            opt_keywords_is_deleted=False
        ).first()
        
        if existing_config:
            existing_config.opt_keywords_keyword = validated_data['opt_keywords_keyword']
            existing_config.opt_keywords_automated_response = validated_data.get(
                'opt_keywords_automated_response', 
                existing_config.opt_keywords_automated_response
            )
            existing_config.save()
            return existing_config
        
        # Create new configuration
        opt_keyword = OptKeyword.objects.create(
            opt_keywords_type=validated_data['opt_keywords_type'],
            opt_keywords_keyword=validated_data['opt_keywords_keyword'],
            opt_keywords_automated_response=validated_data.get('opt_keywords_automated_response', '')
        )
        
        return opt_keyword

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.opt_keywords_keyword = validated_data.get('opt_keywords_keyword', instance.opt_keywords_keyword)
        instance.opt_keywords_automated_response = validated_data.get(
            'opt_keywords_automated_response', 
            instance.opt_keywords_automated_response
        )
        instance.save()
        return instance