from rest_framework import serializers
from apps.role_permissions_management.feature_actions.models import FeatureAction
from apps.role_permissions_management.features.models import Feature
from apps.role_permissions_management.permissions.models import Permission
import uuid
from django.db import transaction

class PermissionSerializer(serializers.Serializer):

    permissions_id = serializers.IntegerField(read_only=True)
    permissions_unique_id = serializers.CharField(read_only=True)
    permissions_created_at = serializers.DateTimeField(read_only=True)
    permissions_updated_at = serializers.DateTimeField(read_only=True)
    permissions_user_roles_keys = serializers.CharField(max_length=50)
    permissions_branches_unique_id = serializers.CharField(max_length=255)
    permissions_features_keys = serializers.CharField(max_length=50)
    permissions_feature_actions_keys = serializers.ListField(
        child=serializers.CharField(max_length=50)
    )
    permissions_can_deleted = serializers.BooleanField(default=False)
    permissions_created_by = serializers.CharField(max_length=255, required=False, allow_null=True)
    permissions_updated_by = serializers.CharField(max_length=255, required=False, allow_null=True)
    permissions_is_active = serializers.BooleanField(default=True)
    permissions_is_deleted = serializers.BooleanField(default=False)
    
    def validate_permissions_features_keys(self, value):
        try:
            Feature.objects.get(features_keys=value, features_is_active=True)
            return value
        except Feature.DoesNotExist:
            raise serializers.ValidationError(f"Feature '{value}' not found or inactive")
    
    def validate_permissions_feature_actions_keys(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("This must be a list of action keys.")
        
        # Get feature key from initial data
        feature_key = self.initial_data.get('permissions_features_keys')
        if not feature_key:
            return value
        
        try:
            feature = Feature.objects.get(features_keys=feature_key)
            valid_actions = FeatureAction.objects.filter(
                feature_actions_features_keys=feature,
                feature_actions_is_active=True
            ).values_list('feature_actions_action_keys', flat=True)
            
            invalid_actions = set(value) - set(valid_actions)
            if invalid_actions:
                raise serializers.ValidationError(
                    f"Invalid actions: {', '.join(invalid_actions)}. "
                    f"Valid actions are: {', '.join(valid_actions)}"
                )
            
            return value
            
        except Feature.DoesNotExist:
            return value
    
    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        
        # Get Feature object
        feature_key = validated_data['permissions_features_keys']
        feature = Feature.objects.get(features_keys=feature_key)
        
        # Create permission
        permission = Permission.objects.create(
            permissions_unique_id=f"PER-{uuid.uuid4().hex[:10].upper()}",
            permissions_user_roles_keys=validated_data['permissions_user_roles_keys'],
            permissions_branches_unique_id=validated_data['permissions_branches_unique_id'],
            permissions_features_keys=feature,
            permissions_feature_actions_keys=validated_data['permissions_feature_actions_keys'],
            permissions_can_deleted=validated_data.get('permissions_can_deleted', False),
            permissions_created_by= validated_data.get('permissions_created_by'),
            permissions_is_active=validated_data.get('permissions_is_active', True),
            permissions_is_deleted=validated_data.get('permissions_is_deleted', False)
        )
        
        return permission
    
    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get('request')
        
        # Update feature if changed
        if 'permissions_features_keys' in validated_data:
            feature_key = validated_data['permissions_features_keys']
            feature = Feature.objects.get(features_keys=feature_key)
            instance.permissions_features_keys = feature
        
        # Update other fields
        for attr, value in validated_data.items():
            if attr not in ['permissions_features_keys', 'permissions_id', 
                          'permissions_unique_id', 'permissions_created_at', 
                          'permissions_updated_at']:
                setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.permissions_features_keys:
            representation['permissions_features_keys'] = instance.permissions_features_keys.features_keys
        
        return representation