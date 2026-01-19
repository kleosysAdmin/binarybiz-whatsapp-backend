from django.db import models

# Create your models here.


KEYWORD_TYPE_CHOICES = [
    ('opt_in', 'Opt-in'),
    ('opt_out', 'Opt-out'),
]

# Model for OptKeyword
class OptKeyword(models.Model):
    opt_keywords_id = models.AutoField(primary_key=True)
    opt_keywords_type = models.CharField(max_length=50, choices=KEYWORD_TYPE_CHOICES, null=True, blank=True)
    opt_keywords_keyword = models.JSONField(default=list, null=True, blank=True)
    opt_keywords_automated_response = models.TextField(null=True, blank=True)
    opt_keywords_is_deleted = models.BooleanField(default=False)
    opt_keywords_created_at = models.DateTimeField(auto_now_add=True)
    opt_keywords_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "opt_keywords"
