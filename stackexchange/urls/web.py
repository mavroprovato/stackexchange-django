"""The web URLs configuration
"""
from django.urls import path

from stackexchange import views


urls = [
    path('', views.IndexView.as_view(), name='web-index'),
    path('questions', views.QuestionView.as_view(), name='web-question-list'),
    path('questions/tagged/<str:tag>', views.QuestionTaggedView.as_view(), name='web-question-tagged'),
    path('questions/<int:pk>', views.QuestionDetailView.as_view(), name='web-question-detail'),
    path('questions/<int:pk>/<slug:slug>', views.QuestionDetailView.as_view(), name='web-question-detail-slug'),
    path('tags', views.TagView.as_view(), name='web-tag-list'),
    path('users', views.UserView.as_view(), name='web-user-list'),
    path('users/<int:pk>', views.UserDetailView.as_view(), name='web-user-detail'),
    path('users/<int:pk>/<str:slug>', views.UserDetailView.as_view(), name='web-user-detail-slug'),
]
