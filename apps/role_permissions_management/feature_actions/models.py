from django.db import models
from apps.role_permissions_management.features.models import Feature
# Create your models here.

class FeatureAction(models.Model):
    feature_actions_id = models.AutoField(primary_key=True)
    feature_actions_keys = models.CharField(max_length=50, unique=True, null=True, blank=True)
    feature_actions_features_keys = models.ForeignKey(Feature, to_field='features_keys', db_column='feature_actions_features_keys', on_delete=models.CASCADE, null=True, blank=True)
    feature_actions_action = models.CharField(max_length=255, null=True, blank=True)
    feature_actions_action_keys = models.CharField(max_length=50, null=True, blank=True)
    feature_actions_is_active = models.BooleanField(default=True)
    feature_actions_created_at = models.DateTimeField(auto_now_add=True)
    feature_actions_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feature_actions'