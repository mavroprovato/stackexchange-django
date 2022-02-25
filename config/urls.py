"""URL configuration
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework import routers

from stackexchange import views

router = routers.DefaultRouter()
router.register('answers', views.AnswerViewSet, basename='answer')
router.register('badges', views.BadgeViewSet, basename='badge')
router.register('comments', views.CommentViewSet, basename='comment')
router.register('info', views.InfoViewSet, basename='info')
router.register('posts', views.PostViewSet, basename='post')
router.register('questions', views.QuestionViewSet, basename='question')
router.register('tags', views.TagViewSet, basename='tag')
router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('__debug__/', include(debug_toolbar.urls)),
]
