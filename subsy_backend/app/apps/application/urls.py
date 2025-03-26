"""
URL mappings for the application app.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.application import views

app_name = 'apps.application'

router = DefaultRouter()

router.register('applications', views.ApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),
]
