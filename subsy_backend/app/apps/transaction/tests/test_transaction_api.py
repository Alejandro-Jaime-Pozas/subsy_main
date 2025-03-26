"""Tests for the transaction api."""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Transaction
from core.tests.shared_data import (
    TEST_TRANSACTION_DATA,
    create_user,
    create_transaction,
)
from apps.transaction.serializers import TransactionSerializer


TRANSACTION_LIST_URL = reverse('apps.transaction:transaction-list')


# transactions are also fetched from plaid api
# user should change nothing about the transaction, all plaid internal

def get_transaction_detail_url(transaction_id):
    return reverse('apps.transaction:transaction-detail', args=[transaction_id])


class PrivateTransactionApiTests(TestCase):
    """All transaction api tests should be private, require existing user(s)."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    # test GET transaction detail for user success
    def test_retrieve_transaction_success(self):
        """Test retrieving transaction for a user's companies is successful."""
        transaction = create_transaction(user=self.user, **TEST_TRANSACTION_DATA)
        transaction_detail_url = get_transaction_detail_url(transaction.id)

        res = self.client.get(transaction_detail_url)

        serializer = TransactionSerializer(transaction)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # test GET transaction list for user success
    def test_list_transactions_success(self):
        """Test listing transactions for a user's companies is successful."""
        create_transaction(user=self.user, **TEST_TRANSACTION_DATA)

        res = self.client.get(TRANSACTION_LIST_URL)

        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    # test GET for unauthorized user fails
    def test_list_transactions_unauthorized(self):
        """Test that listing transactions is not allowed for unauthorized users."""
        transaction = create_transaction(user=self.user, **TEST_TRANSACTION_DATA)  # create a transaction for default user
        user2 = create_user(email='test2@example.com')
        client2 = APIClient()
        client2.force_authenticate(user=user2)

        res = client2.get(get_transaction_detail_url(transaction.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
