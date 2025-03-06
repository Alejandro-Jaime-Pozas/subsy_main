# Create your views here.
import os, json, time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.link_token_transactions import LinkTokenTransactions
from plaid.model.item_remove_request import ItemRemoveRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.country_code import CountryCode
from utils import validate_access_token
from datetime import datetime, timedelta, timezone


PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_REQUIRED_IF_SUPPORTED_PRODUCTS = os.getenv('PLAID_REQUIRED_IF_SUPPORTED_PRODUCTS').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')
# PLAID_SANDBOX_REDIRECT_URI = os.getenv('PLAID_SANDBOX_REDIRECT_URI')

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')
PLAID_REDIRECT_URI = os.getenv('PLAID_REDIRECT_URI')

configuration = Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

required_if_supported_products = []
for req_product in PLAID_REQUIRED_IF_SUPPORTED_PRODUCTS:
    required_if_supported_products.append(Products(req_product))

# Create Link Token
def create_link_token(request):
    # print("PLAID_SANDBOX_REDIRECT_URI:", os.getenv('PLAID_SANDBOX_REDIRECT_URI'))
    # print("PLAID_REDIRECT_URI:", os.getenv('PLAID_REDIRECT_URI'))
    # print("PLAID_REDIRECT_URI:", products)
    try:
        link_token_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())  # will prob need to change user_id?
            ),
            client_name="Subsy - Subscription Manager",
            language="en",
            products=products,
            required_if_supported_products=required_if_supported_products,
            transactions=LinkTokenTransactions(
                days_requested=730  # TEST THIS OUT: THIS SHOULD GO BACK 2 YEARS FOR ALL NEW ITEMS, EXISTING ITEMS COULD REQUIRE TO BE REMOVED BEFORE UPDATING TO 2 YEARS DATA
            ),
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            redirect_uri=os.getenv('PLAID_REDIRECT_URI'),
            # redirect_uri=os.getenv('PLAID_SANDBOX_REDIRECT_URI'),
        )
        link_token_response = plaid_client.link_token_create(link_token_request)
        return JsonResponse(link_token_response.to_dict(), safe=False)
    except plaid.ApiException as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=400)

# Exchange Public Token for Access Token
@csrf_exempt
def exchange_public_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            public_token = data.get("public_token")

            exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
            exchange_response = plaid_client.item_public_token_exchange(exchange_request)  # have access_token and item_id in response

            # Store the access_token in the session (for demo purposes)
            request.session["access_token"] = exchange_response.to_dict()["access_token"]

            get_balance_data = get_balance(request)  # have both item and accounts data, so can create LinkedBank and BankAccounts from here
            return JsonResponse({"success": True})
        except plaid.ApiException as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

# Get Account Balances
@validate_access_token
def get_balance(request, *args, **kwargs):
    try:
        balance_request = AccountsBalanceGetRequest(
            access_token=kwargs["access_token"],
            options={
                "min_last_updated_datetime": datetime.now(timezone.utc) - timedelta(days=1)
            }
        )
        balance_response = plaid_client.accounts_balance_get(balance_request)
        print('access token:', kwargs["access_token"])
        print(balance_response.to_dict())
        return JsonResponse({"Balance": balance_response.to_dict()}, safe=False)
    except plaid.ApiException as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=400)

@validate_access_token
def item_remove_request(request, *args, **kwargs):
    try:
        request = ItemRemoveRequest(access_token=kwargs['access_token'])
        response = plaid_client.item_remove(request)
        # The Item was removed and the access_token is now invalid
        return JsonResponse({"success": response.to_dict()})
    except plaid.ApiException as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=400)

# CSRF Token endpoint for front-end use
def csrf_token(request):
    token = get_token(request)
    return JsonResponse({"csrfToken": token})

# Get Latest Transactions
@validate_access_token
def get_latest_transactions(request, *args, **kwargs):
    # Set cursor to empty to receive all historical updates
    # Provide a cursor from your database if you've previously
    # received one for the Item. Leave null if this is your
    # first sync call for this Item. The first request will
    # return a cursor.
    cursor = ''

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = []  # Removed transaction ids
    has_more = True
    try:
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=kwargs.get("access_token"),
                cursor=cursor,
            )
            response = plaid_client.transactions_sync(request).to_dict()
            cursor = response['next_cursor']
            # If no transactions are available yet, wait and poll the endpoint.
            # Normally, we would listen for a webhook, but the Quickstart doesn't
            # support webhooks. For a webhook example, see
            # https://github.com/plaid/tutorial-resources or
            # https://github.com/plaid/pattern
            if cursor == '':
                time.sleep(2)
                print('Waiting for cursor to be available')
                continue
            # If cursor is not an empty string, we got results,
            # so add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
            # pretty_print_response(response)  # TO VIEW TRANSACTION DETAILS

        # Return the 15 most recent transactions
        latest_transactions = sorted(added, key=lambda t: t['date'])[-15:]
        return JsonResponse({'latest_transactions': added[:15]})  # CHANGE BACK!
            # 'latest_transactions': latest_transactions})  # CHANGE BACK!

    except plaid.ApiException as e:
        print(e)
        error_response = format_error(e)  # can format other errors this same way later
        return JsonResponse(error_response)

# Get Transactions
@validate_access_token
def get_all_transactions(request, *args, **kwargs):
    # Set cursor to empty to receive all historical updates
    # Provide a cursor from your database if you've previously
    # received one for the Item. Leave null if this is your
    # first sync call for this Item. The first request will
    # return a cursor.
    cursor = ''

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = []  # Removed transaction ids
    has_more = True
    counter = 1
    try:
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=kwargs.get("access_token"),
                cursor=cursor,
                options={"days_requested": 730}
            )
            response = plaid_client.transactions_sync(request).to_dict()
            cursor = response['next_cursor']
            # If no transactions are available yet, wait and poll the endpoint.
            # Normally, we would listen for a webhook, but the Quickstart doesn't
            # support webhooks. For a webhook example, see
            # https://github.com/plaid/tutorial-resources or
            # https://github.com/plaid/pattern
            if cursor == '':
                time.sleep(2)
                print('Waiting for cursor to be available')
                continue
            # If cursor is not an empty string, we got results,
            # so add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
            # pretty_print_response(response)  # TO VIEW TRANSACTION DETAILS
            counter += 1
            print('MOVING ON TO CURSOR NUMBER:', str(counter))
            print('has_more equals:', str(has_more))
            print('LEN OF ADDED TRANSACTIONS:', str(len(added)))
            print('access token:', kwargs["access_token"])
            print('='*100)

        all_transactions_response = {
            'added': added,
            'modified': modified,
            'removed': removed,
            'has_more': has_more,
            'cursor': cursor,
        }
        return JsonResponse({'all_transactions': all_transactions_response})
    except plaid.ApiException as e:
        print(e)
        error_response = format_error(e)  # can format other errors this same way later
        return JsonResponse(error_response)

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True, default=str))

def format_error(e):
    response = json.loads(e.body)
    return \
        {'error': {
                    'status_code': e.status,
                    'display_message': response['error_message'],
                    'error_code': response['error_code'],
                    'error_type': response['error_type']
        }}
