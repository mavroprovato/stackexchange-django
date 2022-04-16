"""The API URLs configuration
"""
from rest_framework import routers

from stackexchange import views


router = routers.DefaultRouter()
router.register('answers', views.AnswerViewSet, basename='api-answer')
router.register('badges', views.BadgeViewSet, basename='api-badge')
router.register('comments', views.CommentViewSet, basename='api-comment')
router.register('info', views.InfoViewSet, basename='api-info')
router.register('posts', views.PostViewSet, basename='api-post')
router.register('privileges', views.PrivilegesViewSet, basename='api-privilege')
router.register('questions', views.QuestionViewSet, basename='api-question')
router.register('search', views.SearchViewSet, basename='api-search')
router.register('tags', views.TagViewSet, basename='api-tag')
router.register('users', views.UserViewSet, basename='api-user')
