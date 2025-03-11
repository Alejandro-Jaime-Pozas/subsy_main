"""Tests for the company api."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Company
from core.tests.shared_data import TEST_USER_DATA, TEST_COMPANY_DATA
from apps.company.serializers import CompanySerializer


COMPANIES_LIST_URL = reverse('apps.company:company-list')


# need a user to exist in order for there to exist a company, so all tests private
# create a company
# read a company
# update a company

# create default user for tests
def create_user():
    user = get_user_model().objects.create_user(**TEST_USER_DATA)
    return user

# create default company that can be updated with kwargs
def create_company(users, **kwargs):
    """Create and return a test company."""
    defaults = TEST_COMPANY_DATA.copy()
    defaults.update(kwargs)

    company = Company.objects.create(**defaults)
    company.users.set(users)
    return company


class PublicCompanyApiTetsts(TestCase):
    """Test unauthenticated api tests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_token_required(self):
        """Test auth token is required for company endpoint."""
        res = self.client.get(COMPANIES_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCompanyApiTests(TestCase):
    """All company api tests should be private, require existing user(s)."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.payload = TEST_COMPANY_DATA

    def test_retrieve_companies_success(self):
        """Test retrieving companies for a user is successful."""
        create_company(users=get_user_model().objects.filter(id=self.user.id))
        create_company(
            users=get_user_model().objects.filter(id=self.user.id),
            name='AWS test',
            domain='awstest.com',
        )

        res = self.client.get(COMPANIES_LIST_URL)

        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], sorted(serializer.data, key=lambda co: -co['id']))  # companies are returned in reverse order in viewset
