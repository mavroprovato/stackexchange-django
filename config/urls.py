"""URL configuration
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from rest_framework import routers

from stackexchange import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('__debug__/', include(debug_toolbar.urls)),
]
