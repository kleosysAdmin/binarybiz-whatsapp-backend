from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.role_permissions_management.permissions.models import Permission
from apps.role_permissions_management.features.models import Feature
from apps.role_permissions_management.feature_actions.models import FeatureAction
from apps.role_permissions_management.permissions.serializers import PermissionSerializer
import uuid


class PermissionAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        role_key = request.query_params.get('role_key')
        branch_key = request.headers.get('X-Branch-Key')
        permissions_data = request.data.get('permissions', [])

        if not branch_key or not role_key:
            return Response({
                "success": False,
                "status": 400,
                "message": "role_key and branch_key are required."
            }, status=status.HTTP_400_BAD_REQUEST)
    
        # Deactivate old permissions
        Permission.objects.filter(
            permissions_user_roles_keys=role_key,
            permissions_branches_unique_id=branch_key
        ).update(permissions_is_active=False)

        created_permissions = []
        for perm_data in permissions_data:
            feature_key = perm_data.get('feature_key')
            action_keys = perm_data.get('action_keys', [])

            if not feature_key:
                return Response({
                    "success": False,
                    "status": 400,
                    "message": "Missing feature_key in permission data",
                }, status=status.HTTP_400_BAD_REQUEST)

                
            if not action_keys:
                return Response({
                    "success": False,
                    "status": 400,
                    "message": f"Missing action_keys for feature: {feature_key}",
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                feature = Feature.objects.get(features_keys=feature_key)
            except Feature.DoesNotExist:
                return Response({
                    "success": False,
                    "status": 400,
                    "message": f"Feature '{feature_key}' not found",
                }, status=status.HTTP_400_BAD_REQUEST)

            valid_actions = FeatureAction.objects.filter(
                feature_actions_features_keys=feature,
                feature_actions_is_active=True
            ).values_list('feature_actions_action_keys', flat=True)
            
            invalid_actions = set(action_keys) - set(valid_actions)
            if invalid_actions:
                return Response({
                    "success": False,
                    "status": 400,
                    "message": f"Invalid actions for feature '{feature_key}': {', '.join(invalid_actions)}",
                }, status=status.HTTP_400_BAD_REQUEST)
                
            permission, created = Permission.objects.update_or_create(
                permissions_user_roles_keys=role_key,
                permissions_branches_unique_id=branch_key,
                permissions_features_keys=feature,
                defaults={
                    'permissions_feature_actions_keys': action_keys,
                    'permissions_is_active': True,
                    'permissions_is_deleted': False,
                }
            )

            if created:
                permission.permissions_unique_id = f"PER-{uuid.uuid4().hex[:10].upper()}"
                permission.permissions_created_by = None
                permission.save()
            
            created_permissions.append(permission)

        serializer = PermissionSerializer(created_permissions, many=True, context={"request": request})
            
        return Response({
            "success": True,
            "status": 200,
            "message": "Permissions updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def get(self, request):
        role_key = request.query_params.get('role_key')
        branch_key = request.headers.get('X-Branch-Key')

        if not branch_key:
            return Response({
                "success": False,
                "status": 400,
                "message": "branch key are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not role_key:
            return Response({
                "success": False,
                "status": 400,
                "message": "role key are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        

        # Get all active permissions for this role and branch
        permissions = Permission.objects.filter(
            permissions_user_roles_keys=role_key,
            permissions_branches_unique_id=branch_key,
            permissions_is_active=True,
            permissions_is_deleted=False
        ).select_related('permissions_features_keys')

        # Get all features with their actions
        features = Feature.objects.filter(features_is_active=True).prefetch_related('featureaction_set')

        response_data = []
        for feature in features:
            feature_permission = next(
                (p for p in permissions if p.permissions_features_keys_id == feature.features_keys),
                None
            )

            actions = []
            for action in feature.featureaction_set.filter(feature_actions_is_active=True):
        
                has_permission = feature_permission and action.feature_actions_action_keys in feature_permission.permissions_feature_actions_keys
                
                actions.append({
                    'action_key': action.feature_actions_action_keys,
                    'action_name': action.feature_actions_action,
                    'has_permission': has_permission
                })

            response_data.append({
                'feature_key': feature.features_keys,
                'feature_name': feature.features_name,
                'actions': actions
            })

        return Response({
            "success": True,
            "status": 200,
            "message": "Permissions fetched successfully.",
            "data": response_data
        }, status=status.HTTP_200_OK)
    
