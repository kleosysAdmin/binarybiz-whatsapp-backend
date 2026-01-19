from django.urls import path
from apps.attribute_values.views import AttributeValueListCreateView, AttributeValueDetailView

urlpatterns = [
    path('attribute-value/', AttributeValueListCreateView.as_view(), name='attribute-value-list-create'),
    path('attribute-value/<int:attribute_values_id>/', AttributeValueDetailView.as_view(), name='attribute-value-detail'),
]