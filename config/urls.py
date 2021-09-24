"""URL configuration
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework import routers

import stackexchange.views.answers
import stackexchange.views.badges
import stackexchange.views.comments
import stackexchange.views.questions
import stackexchange.views.posts
import stackexchange.views.tags
import stackexchange.views.users

router = routers.DefaultRouter()
router.register(r'badges', stackexchange.views.badges.BadgeViewSet, basename='Badge')
router.register(r'users', stackexchange.views.users.UserViewSet, basename='User')
router.register(r'tags', stackexchange.views.tags.TagViewSet, basename='Tag')
router.register(r'posts', stackexchange.views.posts.PostViewSet, basename='Post')
router.register(r'questions', stackexchange.views.questions.QuestionViewSet, basename='Question')
router.register(r'answers', stackexchange.views.answers.AnswerViewSet, basename='Answer')
router.register(r'comments', stackexchange.views.comments.CommentViewSet, basename='Comment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('__debug__/', include(debug_toolbar.urls)),
]
