"""The web URLs configuration
"""
from django.urls import path

from stackexchange import views


urls = [
    path('', views.IndexView.as_view(), name='index'),
]
