"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from core import views as core_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # admin view
    path('admin/', admin.site.urls),
    # health check url
    path("api/health-check/", core_views.health_check, name='health-check'),
    # for drf_spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional GUI - spectacualr / swagger - documentation
    path('api/docs/',
         SpectacularSwaggerView.as_view(url_name='schema'),
         name='api-docs'
         ),
    path('api/redoc/',
         SpectacularRedocView.as_view(url_name='schema'),
         name='redocs'
         ),
    # endpoints handling gettting and user creation
    path('api/user/', include('user.urls')),
    # endpoints handling teh recipe API
    path('api/recipe/', include('recipe.urls')),
]

if settings.DEBUG:
    # we are mimiking the bahvaiour of serving media files
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,
    )
