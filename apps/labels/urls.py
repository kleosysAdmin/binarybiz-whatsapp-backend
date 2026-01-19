from django.urls import path

from apps.labels.views import LabelListCreateView , LabelDetailView

urlpatterns = [
    # URL for listing all Labels and creating a new one
    path('label/', LabelListCreateView.as_view(), name='label-list-create'),
    # URL for retrieving, updating, or soft deleting a specific Labels by its ID
    path('label/<int:labels_id>/', LabelDetailView.as_view(), name='label-detail')
]