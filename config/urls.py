"""URL configuration
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
