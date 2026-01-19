from django.db import models

# Create your models here.



# Model for ProfileChatSettings

# Vertical choices
VERTICAL_CHOICES = [
    ('ecommerce', 'ECommerce'),
    ('education', 'Education'),
    ('finance', 'Finance'),
    ('health', 'Health'),
]

class ProfileChatSettings(models.Model):
    profile_chat_settings_id = models.AutoField(primary_key=True)
    profile_chat_settings_profile_picture_path = models.TextField(null=True, blank=True)
    profile_chat_settings_description = models.CharField(max_length=256, null=True, blank=True)
    profile_chat_settings_address = models.CharField(max_length=256, null=True, blank=True)
    profile_chat_settings_email = models.CharField(max_length=256, null=True, blank=True)
    profile_chat_settings_vertical = models.CharField(
        max_length=50, 
        choices=VERTICAL_CHOICES,
        null=True, 
        blank=True
    )
    profile_chat_settings_websites = models.JSONField(default=list, null=True, blank=True)
    profile_chat_settings_auto_resolve = models.BooleanField(default=True)
    profile_chat_settings_welcome_message = models.TextField(null=True, blank=True)
    profile_chat_settings_off_hours_message = models.TextField(null=True, blank=True)
    profile_chat_settings_timezone = models.CharField(max_length=255, null=True, blank=True)
    profile_chat_settings_created_by = models.CharField(max_length=255, null=True, blank=True)
    profile_chat_settings_updated_by = models.CharField(max_length=255, null=True, blank=True)
    profile_chat_settings_is_deleted = models.BooleanField(default=False)
    profile_chat_settings_created_at = models.DateTimeField(auto_now_add=True)
    profile_chat_settings_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profile_chat_settings"


# Model for WorkingHours

# Day choices
DAY_CHOICES = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]

class WorkingHours(models.Model):
    working_hours_id = models.AutoField(primary_key=True)
    working_hours_profile_chat_settings_id = models.ForeignKey(
        ProfileChatSettings,
        to_field="profile_chat_settings_id",
        db_column="working_hours_profile_chat_settings_id",
        on_delete=models.CASCADE, null=True, blank=True
    )
    working_hours_day = models.CharField(max_length=50, choices=DAY_CHOICES, null=True, blank=True)
    working_hours_enabled = models.BooleanField(default=True)
    working_hours_start = models.TimeField(null=True, blank=True)
    working_hours_end = models.TimeField(null=True, blank=True)
    working_hours_created_at = models.DateTimeField(auto_now_add=True)
    working_hours_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "working_hours"

