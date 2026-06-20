"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from accounts.views import refresh_access_token, allusers, change_user_status
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/admin/users/', allusers),
    path('api/admin/users/<uuid:id>/', change_user_status),
    
    # Apps inclusion
    path('api/', include('activities.urls')),
    path('api/', include('test.urls')),
    path('api/', include('accounts.urls')),
    path('api/seances/', include('seance.urls')),
    path('api/children/', include('children.urls')),
    path('api/participants/', include('participants.urls')),
    path('api/schedules/', include('schedules.urls')),
    
    path('api/token/refresh/', refresh_access_token),

    # Downloads raw schema configuration mapping file
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Primary Swagger UI Interactive Web Interface
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Alternative clean reading panel layout documentation
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
