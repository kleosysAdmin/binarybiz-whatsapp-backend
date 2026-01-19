from django.urls import path
from apps.audiences.views import AudienceListCreateView, AudienceDetailView , AudienceImportView , AudienceStatusDetailView

urlpatterns = [
    path('audience/', AudienceListCreateView.as_view(), name='audience-list-create'),
    path('audience/<int:audiences_id>/', AudienceDetailView.as_view(), name='audience-detail'),
    path('audience/<int:audiences_id>/status/', AudienceStatusDetailView.as_view(), name='audience-status-detail'),
    path('audience/import/', AudienceImportView.as_view(), name='audience-import'), 
]   