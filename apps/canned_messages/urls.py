from django.urls import path
from apps.canned_messages.views import (
    CannedMessageListCreateView, 
    CannedMessageDetailView,
    CannedMessageFavouriteView
)

urlpatterns = [
    path('canned-message/', CannedMessageListCreateView.as_view(), name='canned-message-list-create'),
    path('canned-message/<int:canned_messages_id>/', CannedMessageDetailView.as_view(), name='canned-message-detail'),
    path('canned-message/<int:canned_messages_id>/favourite/', CannedMessageFavouriteView.as_view(), name='canned-message-favourite'),
]