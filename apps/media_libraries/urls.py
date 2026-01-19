from django.urls import path
from apps.media_libraries.views import MediaLibraryListCreateView, MediaLibraryDetailView

urlpatterns = [
    path('media/', MediaLibraryListCreateView.as_view(), name='media-list-create'),
    path('media/<int:media_libraries_id>/', MediaLibraryDetailView.as_view(), name='media-detail'),
]