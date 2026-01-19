from django.db import models

# Create your models here.

# Model for Attribute
class Attribute(models.Model):
    attributes_id = models.AutoField(primary_key=True)
    attributes_name = models.CharField(max_length=255, null=True, blank=True)
    attributes_created_by = models.CharField(max_length=255, null=True, blank=True)
    attributes_updated_by = models.CharField(max_length=255, null=True, blank=True)
    attributes_is_active = models.BooleanField(default=True)
    attributes_is_deleted = models.BooleanField(default=False)
    attributes_created_at = models.DateTimeField(auto_now_add=True)
    attributes_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attributes"