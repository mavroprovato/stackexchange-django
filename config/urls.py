"""URL configuration
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework import routers

from stackexchange import views

router = routers.DefaultRouter()
router.register(r'badges', views.BadgeViewSet, basename='Badge')
router.register(r'users', views.UserViewSet, basename='User')
router.register(r'tags', views.TagViewSet, basename='Tag')
router.register(r'posts', views.PostViewSet, basename='Post')
router.register(r'questions', views.QuestionViewSet, basename='Post')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('__debug__/', include(debug_toolbar.urls)),
]
