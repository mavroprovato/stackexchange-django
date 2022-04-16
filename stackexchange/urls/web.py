"""The web URLs configuration
"""
from django.urls import path

from stackexchange import views


urls = [
    path('', views.IndexView.as_view(), name='web-index'),
    path('questions', views.QuestionView.as_view(), name='web-questions'),
    path('questions/tagged/<str:tag>', views.QuestionTaggedView.as_view(), name='web-questions-tagged'),
    path('questions/<int:pk>', views.QuestionDetailView.as_view(), name='web-question-detail'),
    path('tags', views.TagView.as_view(), name='web-tags'),
]
