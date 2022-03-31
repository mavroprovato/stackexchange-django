"""The API URLs configuration
"""
from rest_framework import routers

from stackexchange import views


router = routers.DefaultRouter()
router.register('answers', views.AnswerViewSet, basename='answer')
router.register('badges', views.BadgeViewSet, basename='badge')
router.register('comments', views.CommentViewSet, basename='comment')
router.register('info', views.InfoViewSet, basename='info')
router.register('posts', views.PostViewSet, basename='post')
router.register('privileges', views.PrivilegesViewSet, basename='privileges')
router.register('questions', views.QuestionViewSet, basename='question')
router.register('search', views.SearchViewSet, basename='search')
router.register('tags', views.TagViewSet, basename='tag')
router.register('users', views.UserViewSet, basename='user')
