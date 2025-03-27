"""Test the application API."""

from venv import create
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Application
from core.tests.shared_data import (
    TEST_APPLICATION_DATA,
    create_user,
    create_application,
    create_company,
)
from utils import pretty_print_json

from ..serializers import ApplicationSerializer


APPLICATIONS_URL = reverse('apps.application:application-list')

def create_detail_url(application_id):
    """Return application detail URL."""
    return reverse('apps.application:application-detail', args=[application_id])


# application should be read-only

class PrivateApplicationApiTests(TestCase):
    """Test the application API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test_app@example.com')
        self.client.force_authenticate(self.user)

    def test_retrieve_applications(self):
        """Test retrieving a list of applications."""
        company = create_company(domain='testdomain2.com')
        create_application(
            user=self.user,
            company=company
        )
        company2 = create_company(domain='testdomain3.com')
        create_application(
            user=self.user,
            company=company2
        )
        res = self.client.get(APPLICATIONS_URL)

        applications = Application.objects.all()
        serializer = ApplicationSerializer(applications, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_retrieve_application_detail(self):
        """Test viewing a application detail."""
        application = create_application(user=self.user)
        url = create_detail_url(application.id)
        res = self.client.get(url)

        serializer = ApplicationSerializer(application)

        self.assertEqual(res.data, serializer.data)

    def test_retrieve_applications_limited_to_user(self):
        """Test retrieving applications are limited to user."""
        # create a second user, api client, and applications
        user2 = create_user(email='test2@example.com')
        client2 = APIClient()
        client2.force_authenticate(user2)
        # OG user app
        company = create_company(domain='testdomain2.com')
        user1_app = create_application(
            user=self.user,
            company=company
        )
        # user2 app
        company2 = create_company(domain='user2.com')
        user2_app = create_application(
            user=user2,
            company=company2,
            name='Test App 2'
        )

        url = create_detail_url(user1_app.id)
        res2 = client2.get(url)

        self.assertEqual(res2.status_code, status.HTTP_404_NOT_FOUND)
