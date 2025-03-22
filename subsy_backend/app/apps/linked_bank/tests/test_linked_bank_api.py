from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import LinkedBank
from core.tests.shared_data import (
    TEST_LINKED_BANK_DATA,
    create_user,
)
from apps.linked_bank.serializers import LinkedBankSerializer


LINKED_BANK_LIST_URL = reverse('apps.linked_bank:linked-bank-list')


# test GET linked banks list for user success

# test GET linked bank detail for user success

# test DELETE linked bank for user success

# test GET linked banks list for non-user permission denied error
