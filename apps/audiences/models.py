from django.db import models

# Create your models here.


# Source choices
SOURCE_CHOICES = [
    ('organic', 'Organic'),
    ('imported', 'Imported'),
]

# Opted choices
OPTED_CHOICES = [
    ('in', 'In'),
    ('out', 'Out'),
]


# Model for Audience
class Audience(models.Model):
    audiences_id = models.AutoField(primary_key=True)
    audiences_name = models.CharField(max_length=255, null=True, blank=True)
    audiences_phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    audiences_email = models.CharField(max_length=255, unique=True, null=True, blank=True)
    audiences_source = models.CharField(max_length=50, choices=SOURCE_CHOICES, null=True, blank=True)
    audiences_opted = models.CharField(max_length=50, choices=OPTED_CHOICES, null=True, blank=True)
    audiences_labels = models.JSONField(default=list, null=True, blank=True)
    audiences_last_active = models.DateTimeField(null=True, blank=True)
    audiences_created_by = models.CharField(max_length=255, null=True, blank=True)
    audiences_updated_by = models.CharField(max_length=255, null=True, blank=True)
    audiences_is_active = models.BooleanField(default=True)
    audiences_is_deleted = models.BooleanField(default=False)
    audiences_created_at = models.DateTimeField(auto_now_add=True)
    audiences_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "audiences"