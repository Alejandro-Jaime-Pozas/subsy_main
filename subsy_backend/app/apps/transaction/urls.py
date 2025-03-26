"""
URL mappings for the transaction app.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.transaction import views

app_name = 'apps.transaction'

router = DefaultRouter()

router.register('transactions', views.TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]
