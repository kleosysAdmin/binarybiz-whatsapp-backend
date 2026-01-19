from django.urls import path
from apps.role_permissions_management.feature_actions.views import FeatureActionsListAPIView

urlpatterns = [
    path('features-actions/', FeatureActionsListAPIView.as_view(),name="features-actions-list"),
]

