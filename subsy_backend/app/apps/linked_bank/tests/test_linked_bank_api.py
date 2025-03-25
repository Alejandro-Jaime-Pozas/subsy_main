"""Tests for the linked bank api."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import LinkedBank, Company
from core.tests.shared_data import (
    TEST_LINKED_BANK_DATA,
    create_user,
    create_company,
)
from apps.linked_bank.serializers import LinkedBankSerializer


LINKED_BANK_LIST_URL = reverse('apps.linked_bank:linked-bank-list')


def get_linked_bank_detail_url(linked_bank_id):
    return reverse('apps.linked_bank:linked-bank-detail', args=[linked_bank_id])


def create_linked_bank(company=None, user=None, **kwargs):
    """Create and return a test linked bank."""
    defaults = TEST_LINKED_BANK_DATA.copy()
    defaults.update(kwargs)

    if not company:
        company = create_company()
    if not user:
        user = create_user()

    company.users.add(user)
    linked_bank = LinkedBank.objects.create(company=company, **defaults)
    return linked_bank


class PrivateLinkedBankApiTests(TestCase):
    """All linked bank api tests should be private, require existing user(s)."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    # test GET linked bank detail for user success
    def test_retrieve_linked_bank_success(self):
        """Test retrieving linked bank for a user's companies is successful."""
        linked_bank = create_linked_bank(user=self.user, **TEST_LINKED_BANK_DATA)
        linked_bank_detail_url = get_linked_bank_detail_url(linked_bank.id)

        res = self.client.get(linked_bank_detail_url)

        serializer = LinkedBankSerializer(linked_bank)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # test GET linked banks list for user success
    def test_list_linked_bank_success(self):
        """Test retrieving linked banks for a user's companies is successful."""
        test_company = create_company()
        create_linked_bank(user=self.user, company=test_company, **TEST_LINKED_BANK_DATA)
        test_data_2 = TEST_LINKED_BANK_DATA.copy()
        test_data_2['item_id'] = 'test_item_id_2'
        create_linked_bank(user=self.user, company=test_company, **test_data_2)

        res = self.client.get(LINKED_BANK_LIST_URL)

        linked_banks = LinkedBank.objects.all()
        serializer = LinkedBankSerializer(linked_banks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    # test DELETE linked bank for user success
    def test_delete_linked_bank_success(self):
        """Test deleting linked bank for a user's companies is successful."""
        linked_bank = create_linked_bank(user=self.user, **TEST_LINKED_BANK_DATA)
        linked_bank_detail_url = get_linked_bank_detail_url(linked_bank.id)

        res = self.client.delete(linked_bank_detail_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        res_get = self.client.get(linked_bank_detail_url)

        self.assertEqual(res_get.status_code, status.HTTP_404_NOT_FOUND)

    # test GET linked banks detail for non-user permission denied error
    def test_detail_linked_bank_permission_denied(self):
        """Test retrieving linked banks for a non-auth user returns permission denied error."""
        linked_bank = create_linked_bank(user=self.user)
        linked_bank_detail_url = get_linked_bank_detail_url(linked_bank.id)

        new_user = get_user_model().objects.create_user(
            email='test_email2@example.com'
        )
        unauth_client = APIClient()
        unauth_client.force_authenticate(user=new_user)

        res_unauth = unauth_client.get(linked_bank_detail_url)
        res = self.client.get(linked_bank_detail_url)

        self.assertEqual(res_unauth.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
