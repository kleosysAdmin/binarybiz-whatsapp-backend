from django.db import models

# Create your models here.


# Model for Label
class Label(models.Model):
    labels_id = models.AutoField(primary_key=True)
    labels_name = models.CharField(max_length=255, null=True, blank=True)
    labels_description = models.TextField(null=True, blank=True)
    labels_created_by = models.CharField(max_length=255, null=True, blank=True)
    labels_updated_by = models.CharField(max_length=255, null=True, blank=True)
    labels_is_active = models.BooleanField(default=True)
    labels_is_deleted = models.BooleanField(default=False)
    labels_created_at = models.DateTimeField(auto_now_add=True)
    labels_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "labels"