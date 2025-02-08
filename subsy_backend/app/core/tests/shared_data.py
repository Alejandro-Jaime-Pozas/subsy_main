from ..models import *
from django.contrib.auth import get_user_model

"""Object data for input in django test modules."""

TEST_USER_DATA = {
    'email': 'test@example.com',
    'password': 'deftestpass123',
}

TEST_COMPANY_DATA = {
    'name': 'def Apple',
    'domain': 'defapple.com',
}

TEST_LINKED_BANK_DATA = {
    'item_id': 'defb5P7zNlfZABn9yqjos4zK3yvwD4FqwmNNp',
    'institution_id': 'ins_56',
    'institution_name': 'Chase',
    # company
}

TEST_BANK_ACCOUNT_DATA = {
    "account_id": "defZXwn1mehQnB1RlbwGtJDADWkMkJc4DAwVk",
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

def create_default_instances():
    """Create and return default instances for all db models."""
    user = get_user_model().objects.create_user(**TEST_USER_DATA)
    company = Company.objects.create(**TEST_COMPANY_DATA)
    linked_bank = LinkedBank.objects.create(**TEST_LINKED_BANK_DATA, company=company)
    bank_account = BankAccount.objects.create(**TEST_BANK_ACCOUNT_DATA, linked_bank=linked_bank)

    return {
        'user': user,
        'company': company,
        'linked_bank': linked_bank,
        'bank_account': bank_account,
    }
