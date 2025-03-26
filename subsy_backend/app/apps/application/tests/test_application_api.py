"""Test the application API."""

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
from utils import random_37_char_string

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
        item_id = random_37_char_string()
        create_application(
            user=self.user,
            company=company2
        )
        res = self.client.get(APPLICATIONS_URL)

        applications = Application.objects.all()
        serializer = ApplicationSerializer(applications, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)
