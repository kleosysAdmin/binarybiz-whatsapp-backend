from django.urls import path
from apps.attributes.views import AttributeListCreateView, AttributeDetailView

urlpatterns = [
    path('attribute/', AttributeListCreateView.as_view(), name='attribute-list-create'),
    path('attribute/<int:attributes_id>/', AttributeDetailView.as_view(), name='attribute-detail'),
]