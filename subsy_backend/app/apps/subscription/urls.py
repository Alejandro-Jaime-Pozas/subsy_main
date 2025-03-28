"""
URL mappings for the subscription app.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.subscription import views

app_name = 'apps.subscription'

router = DefaultRouter()

router.register('subscriptions', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
