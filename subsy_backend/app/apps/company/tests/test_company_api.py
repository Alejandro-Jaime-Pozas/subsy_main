"""Tests for the company api."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Company
from core.tests.shared_data import TEST_USER_DATA, TEST_COMPANY_DATA
# from company.serializers import CompanySerializer


COMPANIES_LIST_URL = reverse('apps.company:company-list')


# need a user to exist in order for there to exist a company, so all tests private
# create a company
# read a company
# update a company

# create default company that can be updated with kwargs
def create_company(users, **kwargs):
    """Create and return a test company."""
    defaults = TEST_COMPANY_DATA.copy()
    defaults.update(kwargs)

    company = Company.objects.create(users=users, **defaults)
    return company


class PublicCompanyApiTetsts(TestCase):
    """Test unauthenticated api tests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_token_required(self):
        """Test auth token is required for company endpoint."""
        res = self.client.get(COMPANIES_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateCompanyApiTests(TestCase):
#     """All company api tests should be private, require existing user."""

#     @classmethod
#     def setUpTestData(cls):
#         cls.client = APIClient()
#         # cls.user_token = cls.client.post()

#     def setUp(self):
#         self.payload = {
#             'name': 'Apple',
#             'domain': 'apple.com',
#         }

#     def test_create_company_success(self):
#         """Test creating a company is successful."""
#         # need a linked user's token
