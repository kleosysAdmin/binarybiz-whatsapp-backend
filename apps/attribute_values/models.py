from django.db import models

from apps.audiences.models import Audience
from apps.attributes.models import Attribute

# Create your models here.


# Model for AttributeValue
class AttributeValue(models.Model):
    attribute_values_id = models.AutoField(primary_key=True)
    attribute_values_attributes_id = models.ForeignKey(
        Attribute,
        to_field="attributes_id", 
        db_column="attribute_values_attributes_id",
        on_delete=models.CASCADE, null=True, blank=True
    )
    attribute_values_audiences_id = models.ForeignKey(
        Audience,
        to_field="audiences_id",
        db_column="attribute_values_audiences_id",
        on_delete=models.CASCADE, null=True, blank=True
    )
    attribute_values_value = models.CharField(max_length=255, null=True, blank=True)
    attribute_values_created_by = models.CharField(max_length=255, null=True, blank=True)
    attribute_values_updated_by = models.CharField(max_length=255, null=True, blank=True)
    attribute_values_is_deleted = models.BooleanField(default=False)
    attribute_values_created_at = models.DateTimeField(auto_now_add=True)
    attribute_values_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attribute_values"