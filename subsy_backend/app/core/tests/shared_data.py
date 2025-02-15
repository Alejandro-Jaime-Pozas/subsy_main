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
    "balances_currency_code": "USD",
    "name": "Plaid Checking",
    "official_name": "Plaid Gold Standard 0% Interest Checking",
    "type": "depository",
    "subtype": "checking",
    # "linked_bank": test_linked_bank
}

TEST_TRANSACTION_DATA = {
    "transaction_id": "defjeW1nR6CDn5okmGQ6hEpMo4lLNoSrzqDje",
    "account_id": "defXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
    "account_owner": None,
    "amount": 72.1,
    "counterparties": [
        {
            "name": "Walmart",
            "type": "merchant",
            "logo_url": "https://plaid-merchant-logos.plaid.com/walmart_1100.png",
            "website": "walmart.com",
            "entity_id": "O5W5j4dN9OR3E6ypQmjdkWZZRoXEzVMz2ByWM",
            "confidence_level": "VERY_HIGH"
        }
    ],
    "datetime": "2023-09-24T11:01:01Z",
    "currency_code": "USD",
    "logo_url": "https://plaid-merchant-logos.plaid.com/walmart_1100.png",
    "merchant_name": "Walmart",
    "name": "PURCHASE WM SUPERCENTER #1700",
    "payment_channel": "in store",
    "pending": False,
    "personal_finance_category": {
        "primary": "GENERAL_MERCHANDISE",
        "detailed": "GENERAL_MERCHANDISE_SUPERSTORES",
        "confidence_level": "VERY_HIGH"
    },
    "personal_finance_category_icon_url": "https://plaid-category-icons.plaid.com/PFC_GENERAL_MERCHANDISE.png",
    "website": "walmart.com",
    # "bank_account": test_bank_account
}

def create_default_instances():
    """Create and return default instances for all db models."""
    user = get_user_model().objects.create_user(**TEST_USER_DATA)
    company = Company.objects.create(**TEST_COMPANY_DATA)
    linked_bank = LinkedBank.objects.create(**TEST_LINKED_BANK_DATA, company=company)
    bank_account = BankAccount.objects.create(**TEST_BANK_ACCOUNT_DATA, linked_bank=linked_bank)
    transaction = Transaction.objects.create(**TEST_TRANSACTION_DATA, bank_account=bank_account)

    return {
        'user': user,
        'company': company,
        'linked_bank': linked_bank,
        'bank_account': bank_account,
        'transaction': transaction,
    }
