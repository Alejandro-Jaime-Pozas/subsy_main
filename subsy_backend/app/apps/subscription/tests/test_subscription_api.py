"""Test the subscription API."""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Subscription


from utils import pretty_print_json

from ..serializers import SubscriptionSerializer


SUBSCRIPTIONS_URL = reverse('apps.subscription:subscription-list')

def create_detail_url(subscription_id):
    """Return subscription detail URL."""
    return reverse('apps.subscription:subscription-detail', args=[subscription_id])


# 
