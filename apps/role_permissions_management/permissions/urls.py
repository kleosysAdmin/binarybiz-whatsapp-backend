from django.urls import path
from apps.role_permissions_management.permissions.views import PermissionAPIView



urlpatterns = [
    path('permissions/', PermissionAPIView.as_view(), name='permission-list-manage'),
]