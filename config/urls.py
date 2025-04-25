"""
URL configuration for stackexchange-django project.

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
from django.urls import path, include
import debug_toolbar
from drf_spectacular import views

from stackexchange.urls import api, web

urlpatterns = [
    path('', include(web.urls)),
    path('api/', include(api.router.urls)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/doc/', views.SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', views.SpectacularAPIView.as_view(), name='schema'),
    path('__debug__/', include(debug_toolbar.urls)),
]
