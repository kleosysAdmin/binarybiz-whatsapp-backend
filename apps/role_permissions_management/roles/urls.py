from django.urls import path
from apps.role_permissions_management.roles.views import UserRoleListCreateView, UserRoleDetailView

urlpatterns = [
    path('roles/', UserRoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<str:user_roles_keys>/', UserRoleDetailView.as_view(), name='role-detail-view'),
]
