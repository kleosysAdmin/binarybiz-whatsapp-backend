from django.urls import path
from apps.profile_chat_settings.views import ProfileChatSettingsDetailView

urlpatterns = [
    path('profile-chat-settings/<int:profile_chat_settings_id>/', ProfileChatSettingsDetailView.as_view(), name='profile-chat-settings-detail'),
]