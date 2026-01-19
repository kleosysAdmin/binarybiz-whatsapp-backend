"""
URL configuration for binarybiz_whatsapp_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/',include('apps.labels.urls')),
    path('api/v1/',include('apps.attributes.urls')),
    path('api/v1/',include('apps.attribute_values.urls')),
    path('api/v1/',include('apps.audiences.urls')),
    path('api/v1/',include('apps.canned_messages.urls')),
    path('api/v1/',include('apps.media_libraries.urls')),
    path('api/v1/',include('apps.profile_chat_settings.urls')),
    path('api/v1/',include('apps.opt_keywords.urls')),
    path('api/v1/', include('apps.role_permissions_management.permissions.urls')),
    path('api/v1/', include('apps.role_permissions_management.roles.urls')),
    path('api/v1/', include('apps.role_permissions_management.feature_actions.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
