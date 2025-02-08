from ..models import *
from django.contrib.auth import get_user_model

"""Object data for input in django test modules."""

TEST_USER_DATA = {
    'email': 'test@example.com',
    'password': 'testpass123',
}

TEST_COMPANY_DATA = {
    'name': 'Apple',
    'domain': 'apple.com',
}

TEST_LINKED_BANK_DATA = {
    'item_id': '3eWb5P7zNlfZABn9yqjos4zK3yvwD4FqwmNNp',
    'institution_id': 'ins_56',
    'institution_name': 'Chase',
    # company
}

TEST_BANK_ACCOUNT_DATA = {
    "account_id": "BzqZXwn1mehQnB1RlbwGtJDADWkMkJc4DAwVk",
    "balances_available": 100,
    "balances_current": 110,
    "balances_limit": None,
    "balances_iso_currency_code": "USD",
    "name": "Plaid Checking",
    "official_name": "Plaid Gold Standard 0% Interest Checking",
    "type": "depository",
    "subtype": "checking",
    # "linked_bank": test_linked_bank
}


def create_user():
    return get_user_model().objects.create_user(**TEST_USER_DATA)

def create_company():
    return Company.objects.create(**TEST_COMPANY_DATA)

def create_linked_bank():
    return LinkedBank.objects.create(**TEST_LINKED_BANK_DATA)

def create_bank_account():
    return BankAccount.objects.create(**TEST_BANK_ACCOUNT_DATA)
