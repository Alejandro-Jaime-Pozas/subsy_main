"""Test the subscription API."""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Subscription
from core.tests.shared_data import create_application, create_company, create_subscription, create_user

from utils import pretty_print_json

from ..serializers import SubscriptionSerializer


SUBSCRIPTIONS_URL = reverse('apps.subscription:subscription-list')

def create_detail_url(subscription_id):
    """Return subscription detail URL."""
    return reverse('apps.subscription:subscription-detail', args=[subscription_id])


# user should be able to CRUD subscriptions? since our app could be wrong and they can fix it
class PrivateSubscriptionApiTests(TestCase):
    """Test the subscription API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='sub_test_user@example.com')
        self.client.force_authenticate(self.user)

    # test GET a subscription
    def test_retrieve_subscription_success(self):
        """Test retrieving a subscription."""
        subscription = create_subscription(user=self.user,)

        url = create_detail_url(subscription.id)
        res = self.client.get(url)

        subscription = Subscription.objects.get(id=res.data['id'])
        serializer = SubscriptionSerializer(subscription)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # test GET all subscriptions
    def test_retrieve_subscriptions_success(self):
        """Test retrieving all subscriptions."""
        subscription1 = create_subscription(
            user=self.user,
        )
        company2 = create_company(domain='example2.com')
        subscription2 = create_subscription(
            user=self.user,
            company=company2,
        )

        url = SUBSCRIPTIONS_URL
        res = self.client.get(url)

        subscriptions = Subscription.objects.all()
        serializer = SubscriptionSerializer(subscriptions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    # test PATCH a subscription
    def test_partial_update_subscription_success(self):
        """Test updating a subscription."""
        subscription = create_subscription(
            user=self.user,
        )
        payload = {
            'active': False,
        }

        url = create_detail_url(subscription.id)
        res = self.client.patch(url, payload)

        subscription.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(subscription.active, payload['active'])

    # test subscription for a user that isn't authorized returns error
    def test_user_unauth_subscription_error(self):
        """Test that a user that isn't authorized returns an error."""
        subscription = create_subscription(user=self.user)

        user2 = create_user()
        client2 = APIClient()
        client2.force_authenticate(user2)

        url = create_detail_url(subscription.id)
        res = client2.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
