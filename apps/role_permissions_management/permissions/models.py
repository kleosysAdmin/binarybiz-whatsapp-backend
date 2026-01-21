from django.db import models
from apps.role_permissions_management.features.models import Feature
from apps.role_permissions_management.permissions.managers import PermissionManager

# Create your models here.

class Permission(models.Model):
    permissions_id = models.AutoField(primary_key=True)
    permissions_unique_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    permissions_branches_unique_id = models.CharField(max_length=255, null=True, blank=True)
    permissions_user_roles_keys = models.CharField(max_length=50, null=True, blank=True) 
    permissions_features_keys = models.ForeignKey(Feature, to_field='features_keys', db_column='permissions_features_keys', on_delete=models.CASCADE, null=True, blank=True)
    permissions_feature_actions_keys = models.JSONField(default=list, null=True, blank=True)
    permissions_can_deleted = models.BooleanField(default=False)
    permissions_created_by = models.CharField(max_length=255, null=True, blank=True)
    permissions_updated_by = models.CharField(max_length=255, null=True, blank=True)
    permissions_is_active = models.BooleanField(default=True)
    permissions_is_deleted = models.BooleanField(default=False)
    permissions_created_at = models.DateTimeField(auto_now_add=True)
    permissions_updated_at = models.DateTimeField(auto_now=True)

    objects = PermissionManager()

    class Meta:
        db_table = 'permissions'