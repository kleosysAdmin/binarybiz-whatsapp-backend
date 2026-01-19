from django.db import models

# Create your models here.

class Feature(models.Model):
    features_id = models.AutoField(primary_key=True)
    features_keys = models.CharField(max_length=50, unique=True, null=True, blank=True)
    features_name = models.CharField(max_length=255, null=True, blank=True)
    features_is_active = models.BooleanField(default=True)
    features_created_at = models.DateTimeField(auto_now_add=True)
    features_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'features'


        