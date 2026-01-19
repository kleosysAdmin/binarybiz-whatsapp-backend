
from django.db import models

class PermissionManager(models.Manager):
    def get_role_branch_permissions(self, role_key, branch_key, feature_key=None):
        queryset = self.filter(
            permissions_user_roles_keys=role_key,
            permissions_branches_unique_id=branch_key,
            permissions_is_active=True,
            permissions_is_deleted=False
        )
        
        if feature_key:
            queryset = queryset.filter(permissions_features_keys=feature_key)
        return queryset