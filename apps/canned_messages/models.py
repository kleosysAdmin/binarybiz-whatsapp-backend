from django.db import models

# Create your models here.


# Message type choices
MESSAGE_TYPE_CHOICES = [
    ('text', 'Text'),
]

# Model for CannedMessage
class CannedMessage(models.Model):
    canned_messages_id = models.AutoField(primary_key=True)
    canned_messages_name = models.CharField(max_length=255, null=True, blank=True)
    canned_messages_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES, null=True, blank=True)
    canned_messages_description = models.TextField(null=True, blank=True)
    canned_messages_is_favourite = models.BooleanField(default=False)
    canned_messages_created_by = models.CharField(max_length=255, null=True, blank=True)
    canned_messages_updated_by = models.CharField(max_length=255, null=True, blank=True)
    canned_messages_is_deleted = models.BooleanField(default=False)
    canned_messages_created_at = models.DateTimeField(auto_now_add=True)
    canned_messages_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "canned_messages"