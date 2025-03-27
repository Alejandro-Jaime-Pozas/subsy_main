from ..models import *
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone

from utils import random_37_char_string

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
    'access_token': 'sandbox-5b5b5b5b-5b5b-5b5b-5b5b-5b5b5b5b5b5b',
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

TEST_APPLICATION_DATA = {
    "name": "Amazon Web Services",
    'related_names': ['AWS'],
    "website": "https://aws.amazon.com/",
    # "manage_subscription_link": "https://aws.amazon.com/billing",
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

default_datetime = datetime.now(timezone.utc)

TEST_SUBSCRIPTION_DATA = {
    "start_date": default_datetime - timedelta(days=7),
    "end_date": default_datetime,
    "active": True,
    "payment_period": 'Weekly',
    "payment_type": 'Fixed',
    "last_payment_date": default_datetime - timedelta(days=7),
    "next_payment_date": default_datetime,
    # "application": application,
    # "subscription_manager": user
}

TEST_TAG_DATA = {
    "name": 'productivity'
    # "subscriptions": subscription
}

def create_default_instances():
    """Create and return default instances for all db models."""
    user = get_user_model().objects.create_user(**TEST_USER_DATA)
    company = Company.objects.create(**TEST_COMPANY_DATA)
    linked_bank = LinkedBank.objects.create(**TEST_LINKED_BANK_DATA, company=company)
    bank_account = BankAccount.objects.create(**TEST_BANK_ACCOUNT_DATA, linked_bank=linked_bank)
    application = Application.objects.create(**TEST_APPLICATION_DATA)
    transaction = Transaction.objects.create(
        **TEST_TRANSACTION_DATA,
        bank_account=bank_account,
        application=application,
    )
    subscription = Subscription.objects.create(
        **TEST_SUBSCRIPTION_DATA,
        application=application,
        subscription_manager=user,
    )
    tag = Tag.objects.create(**TEST_TAG_DATA)
    tag.subscriptions.add(subscription)

    return {
        'user': user,
        'company': company,
        'linked_bank': linked_bank,
        'bank_account': bank_account,
        'transaction': transaction,
        'application': application,
        'subscription': subscription,
        'tag': tag,
    }


def create_user(**kwargs):
    """Create and return a user instance."""
    user_data = TEST_USER_DATA.copy()
    user_data.update(**kwargs)
    user = get_user_model().objects.create_user(**user_data)
    return user

def create_company(**kwargs):
    """Create and return a company instance."""
    company_data = TEST_COMPANY_DATA.copy()
    company_data.update(**kwargs)
    company = Company.objects.create(**company_data)
    return company

def create_linked_bank(**kwargs):
    """Create and return a linked bank instance."""
    company = kwargs.pop('company', None) or create_company()
    user = kwargs.pop('user', None) or create_user()
    company.users.add(user)
    linked_bank_data = TEST_LINKED_BANK_DATA.copy()
    linked_bank_data['item_id'] = kwargs.get('item_id') or random_37_char_string()  # unique
    linked_bank = LinkedBank.objects.create(**linked_bank_data, company=company)
    return linked_bank

def create_bank_account(**kwargs):
    """Create and return a bank account instance."""
    linked_bank = kwargs.pop('linked_bank', None) or create_linked_bank(**kwargs)
    test_bank_acct_data = TEST_BANK_ACCOUNT_DATA.copy()
    test_bank_acct_data['account_id'] = kwargs.pop('account_id', None) or random_37_char_string()  # unique
    bank_account = BankAccount.objects.create(**test_bank_acct_data, linked_bank=linked_bank)
    return bank_account

def create_transaction(**kwargs):
    """Create and return a transaction instance."""
    bank_account = kwargs.pop('bank_account', None) or create_bank_account(**kwargs)
    application_data = TEST_APPLICATION_DATA.copy()
    application_data['name'] = kwargs.pop('name', None) or 'Test Application ' + random_37_char_string()
    transaction_data = TEST_TRANSACTION_DATA.copy()
    transaction_data['transaction_id'] = kwargs.pop('transaction_id', None) or random_37_char_string()  # unique
    transaction = Transaction.objects.create(
        **transaction_data,
        bank_account=bank_account,
    )
    return transaction

def create_application(**kwargs):
    """
    Create and return an application instance.

    Input the name field to set the application name.
    """
    application_data = TEST_APPLICATION_DATA.copy()
    application_data['name'] = kwargs.pop('name', None) or 'Test Application ' + random_37_char_string()
    transaction = kwargs.pop('transaction', None) or create_transaction(**kwargs)
    application = Application.objects.create(**application_data)
    application.transactions.add(transaction)
    return application
