from django.urls import path
from apps.opt_keywords.views import (
    OptKeywordListCreateView,
    OptKeywordDetailView
)

urlpatterns = [
    # List all opt keywords and create new ones
    path('opt-keyword/', OptKeywordListCreateView.as_view(), name='opt-keyword-list-create'),
    # Detail view for specific opt type (opt_in or opt_out)
    path('opt-keyword/<str:opt_type>/', OptKeywordDetailView.as_view(), name='opt-keyword-detail'),
]