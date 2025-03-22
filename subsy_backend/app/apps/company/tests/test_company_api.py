"""Tests for the company api."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Company
from core.tests.shared_data import (
    TEST_COMPANY_DATA,
    create_user,
)
from apps.company.serializers import CompanySerializer


COMPANIES_LIST_URL = reverse('apps.company:company-list')

# create detail url
def get_company_detail_url(company_id):
    return reverse('apps.company:company-detail', args=[company_id])

# need a user to exist in order for there to exist a company, so all tests private

# create default company that can be updated with kwargs
def create_company(users=None, **kwargs):
    """Create and return a test company."""
    defaults = TEST_COMPANY_DATA.copy()
    defaults.update(kwargs)

    company = Company.objects.create(**defaults)
    company.users.set(users)
    return company


class PublicCompanyApiTests(TestCase):
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

# test GET companies success (multiple)
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
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], sorted(serializer.data, key=lambda co: co['id']))  # companies are returned in reverse order in viewset

    # test POST company success
    def test_create_company_success(self):
        """Test that creating a company success."""
        payload = TEST_COMPANY_DATA.copy()
        payload['users'] = [self.user.id, ]

        res = self.client.post(COMPANIES_LIST_URL, payload)

        company = Company.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['users'], [self.user.id])
        for k, v in payload.items():
            if k != 'users':
                self.assertEqual(getattr(company, k), v)

    # test GET company detail success
        # will need to check how routers create url detail endpoint to create reverse url lookup constant vs COMPANY_LIST_URL
    def test_retrieve_company_detail(self):
        """Test retrieving company detail success."""
        company = create_company(users=get_user_model().objects.filter(id=self.user.id))

        company_detail_url = get_company_detail_url(company.id)
        res = self.client.get(company_detail_url)

        serializer = CompanySerializer(company)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # test GET company NOT from user returns permission error
    def test_company_not_assigned_to_user(self):
        """Test that a company not assigned to the user returns permission error."""
        user2 = get_user_model().objects.create_user(
            email='harry@example.com'
        )
        company = create_company(users=get_user_model().objects.filter(id=user2.id))

        res = self.client.get(get_company_detail_url(company.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'], 'You do not have permission to view this company.')
