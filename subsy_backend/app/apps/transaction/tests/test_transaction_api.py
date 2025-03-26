"""Tests for the transaction api."""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Transaction, Company, Application, BankAccount
from core.tests.shared_data import (
    TEST_TRANSACTION_DATA,
    create_user,
)
from apps.transaction.serializers import TransactionSerializer


TRANSACTION_LIST_URL = reverse('apps.transaction:transaction-list')


# transactions are also fetched from plaid api
# 
