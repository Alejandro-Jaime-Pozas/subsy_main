"""
URL mappings for the linked_bank app.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.linked_bank import views

app_name = 'apps.linked_bank'

router = DefaultRouter()

router.register('linked-banks', views.LinkedBankView, basename='linked-bank')

urlpatterns = [
    path('', include(router.urls)),
]
