"""Object data for input in django test modules."""

test_company_data = {'name': 'Apple', 'domain': 'apple.com'}

def linked_bank():
    return LinkedBank.objects.create(
        company=test_company,
        item_id='3eWb5P7zNlfZABn9yqjos4zK3yvwD4FqwmNNp',
        institution_id='ins_56',
        institution_name='Chase',
    )

setup_bank_account_dict = {
    "account_id": "BzqZXwn1mehQnB1RlbwGtJDADWkMkJc4DAwVk",
    "balances_available": 100,
    "balances_current": 110,
    "balances_limit": None,
    "balances_iso_currency_code": "USD",
    "name": "Plaid Checking",
    "official_name": "Plaid Gold Standard 0% Interest Checking",
    "type": "depository",
    "subtype": "checking",
    "linked_bank": test_linked_bank
}

bank_account_dict = {
    "account_id": "AzqZXwn1mehQnB1RlbwGtJDADWkMkJc4DAwVw",
    "balances_available": 200,
    "balances_current": 150,
    "balances_limit": None,
    "balances_iso_currency_code": "USD",
    "name": "Plaid Checking",
    "official_name": "Plaid Gold Standard 0% Interest Checking",
    "type": "depository",
    "subtype": "checking",
    "linked_bank": test_linked_bank
}
