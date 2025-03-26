"""Tests for the bank account api."""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from utils import pretty_print_json

from core.models import BankAccount
from core.tests.shared_data import (
    TEST_BANK_ACCOUNT_DATA,
    create_user,
    create_bank_account,
)
from ..serializers import BankAccountSerializer


BANK_ACCOUNT_LIST_URL = reverse('apps.bank_account:bank-account-list')


# what do i need for bank accounts?
# bank acct is basically chase checking, or chase credit, or chase savings
# all CRUD?
# since bank acct is fetched directly when plaid item is created, shouldn't be a way to create, delete, or update. all of this is done in the backend by plaid
# so only need to test GET funcitonality

def get_bank_account_detail_url(bank_account_id):
    return reverse('apps.bank_account:bank-account-detail', args=[bank_account_id])


class PrivateBankAccountApiTests(TestCase):
    """Test retrieving user bank account details with api."""

    def setUp(self):

        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    # test GET bank account detail for user success
    def test_get_detail_bank_account_success(self):
        """Test that a user can retrieve a bank account."""
        bank_account = create_bank_account(user=self.user, **TEST_BANK_ACCOUNT_DATA)
        bank_account_detail_url = get_bank_account_detail_url(bank_account.id)

        res = self.client.get(bank_account_detail_url)

        serializer = BankAccountSerializer(bank_account)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # test GET bank account list for user success
    def test_list_bank_accounts_success(self):
        """Test that a user can retrieve their bank accounts."""
        bank_account1 = create_bank_account(user=self.user, **TEST_BANK_ACCOUNT_DATA)
        bank_account2 = create_bank_account(
            user=self.user,
            company=bank_account1.linked_bank.company,
            linked_bank=bank_account1.linked_bank,
        )

        res = self.client.get(BANK_ACCOUNT_LIST_URL)

        bank_accounts = BankAccount.objects.all()
        serializer = BankAccountSerializer(bank_accounts, many=True)  # many=True overrides create detail to create list objects

        # pretty_print_json(res.data['results'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    # test GET bank account for unauthorized user returns 404 not found.
