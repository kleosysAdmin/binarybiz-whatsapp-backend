from django.db import models

# Create your models here.


# Media type choices
MEDIA_TYPE_CHOICES = [
    ('image', 'Image'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('file', 'File'),
]

# Model for MediaLibrary
class MediaLibrary(models.Model):
    media_libraries_id = models.AutoField(primary_key=True)
    media_libraries_file_path = models.TextField(null=True, blank=True)
    media_libraries_file_size = models.BigIntegerField(null=True, blank=True)
    media_libraries_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES, null=True, blank=True)
    media_libraries_is_deleted = models.BooleanField(default=False)
    media_libraries_created_at = models.DateTimeField(auto_now_add=True)
    media_libraries_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "media_libraries"