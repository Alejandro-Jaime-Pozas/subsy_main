"""Tests for the bank account api."""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import BankAccount
from core.tests.shared_data import (
    TEST_BANK_ACCOUNT_DATA,
    create_user,
)
from bank_account.serializers import BankAccountSerializer


BANK_ACCOUNT_LIST_URL = reverse('bank_account:bank-account-list')


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
    def test_list_bank_accounts_success(self):
        """Test that a user can retrieve their bank accounts."""

    # test GET bank account detail for user success


    # test GET bank account for unauthorized user returns 404 not found.
