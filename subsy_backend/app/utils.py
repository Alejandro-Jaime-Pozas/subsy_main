from functools import wraps
from django.http import JsonResponse
import random, string, json

# WRAPPER FUNCTIONS FOR PLAID VIEWS

def validate_access_token(view_func):
    """Wrapper function that checks if user has a valid access token."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.session.get("access_token")  # will need to fetch this from db later
        # print('got access token from request in wrapper fn:', access_token)
        if not access_token:
            return JsonResponse({'error': 'Access token not available.'}, status=403)
        kwargs["access_token"] = access_token
        return view_func(request, *args, **kwargs)
    return wrapper

# FUNCTIONS FOR USE IN VIEWS
def extract_balance_fields_for_plaid_bank_account(balances):
    """
    Extracts balance fields from Plaid bank account data.

    iso_currency_code and unofficial_currency_code from plaid:
    one or the other is always null.
    """
    return {
        'balances_available': balances.get('available'),
        'balances_current': balances.get('current'),
        'balances_limit': balances.get('limit'),
        'balances_currency_code':
            balances.get('iso_currency_code') or \
            balances.get('unofficial_currency_code'),
    }

# FUNCTIONS FOR USE IN TESTS

def random_37_char_string():
    return 'e' + ''.join(random.choices(string.ascii_letters + string.digits, k=36))


def pretty_print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=4, sort_keys=True))

# CONSTANTS FOR USE IN TESTS

SUBSCRIPTION_PAYMENT_PERIOD_CHOICES = [
    ('D', 'Daily'),
    ('W', 'Weekly'),
    ('M', 'Monthly'),
    ('Q', 'Quarterly'),
    ('Y', 'Yearly'),
    ('VAR', 'Variable'),
]

SUBSCRIPTION_PAYMENT_TYPE_CHOICES = [
    ('F', 'Fixed'),
    ('V', 'Variable'),
]
