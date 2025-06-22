# Create your views here.
import os, json, time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.core.exceptions import ObjectDoesNotExist
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
from apps.bank_account.serializers import BankAccountSerializer
from apps.linked_bank.serializers import LinkedBankSerializer
from apps.transaction.serializers import TransactionSerializer
from utils import (
    extract_balance_fields_for_plaid_bank_account,
    merge_currency_codes,
    validate_access_token,
    filter_model_fields,
)
from datetime import datetime, timedelta, timezone

from core.models import (
    BankAccount,
    LinkedBank,
    Transaction,
    Application,
)
from core.tests.shared_data import create_company


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
        # print(e)  # Uncomment for debugging
        return JsonResponse({"error": str(e)}, status=400)


# Exchange Public Token for Access Token
@csrf_exempt
def exchange_public_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            public_token = data.get("public_token")

            exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
            exchange_response = plaid_client.item_public_token_exchange(exchange_request)  # has access_token and item_id in response

            # Store the access_token in the session (for demo purposes)
            # WILL NEED TO STORE ACTUAL ACCESS TOKEN LATER IN GET BALANCE FOR THE ITEM
            request.session["access_token"] = exchange_response.to_dict()["access_token"]

            # get_balance_data = get_balance(request)  # have both item and accounts data, so can create LinkedBank and BankAccounts from here
            return JsonResponse({"success": True})
        except plaid.ApiException as e:
            # print(e)  # Uncomment for debugging
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Get Account Balances
# logged in user with their related company and accesss token will be passed in
@validate_access_token
def get_balance(request, *args, **kwargs):
    try:
        balance_request = AccountsBalanceGetRequest(
            access_token=kwargs["access_token"],  # replace this with USER/ITEM access_token
            options={
                "min_last_updated_datetime": datetime.now(timezone.utc) - timedelta(days=1)
            }
        )
        balance_response = plaid_client.accounts_balance_get(balance_request)
        # pretty_print_response(balance_response.to_dict())
        # ========================================================================
        # TODO SHOULD CREATE SEPARATE ENDPOINT. THIS ONE FOR GETTING PLAID BALANCE, ANOTHER FOR CREATING SUBSY LINKED BANK AND BANK ACCOUNTS, AND THEN ANOTHER FOR GETTING SUBSY LINKED BANK AND BANK ACCOUNTS
        # ========================================================================
        # need to create LinkedBank and BankAccounts from this data
        balance_response_dict = balance_response.to_dict()  # converts json into dict
        linked_bank = balance_response_dict.get("item", {})
        bank_accounts = balance_response_dict.get("accounts", [])
        # pretty_print_response(bank_accounts)
        # pretty_print_response(linked_bank)
        company = create_company()  # TODO REPLACE FOR TESTING PURPOSES ONLY, WILL NEED TO GET ACTUAL COMPANY LATER
        # request.user.companies.add(company)  # WILL NEED TO ADD LATER ONCE USER AUTHENTICATION IS SET UP
        filtered_linked_bank_data = filter_model_fields(LinkedBank, linked_bank)
        saved_linked_bank, created = LinkedBank.objects.get_or_create(
            item_id=filtered_linked_bank_data.pop("item_id"),  # this ensures get_or_create checks for duplicates using item_id and company, not the defaults
            company=company,
            defaults=filtered_linked_bank_data
        )  # WATCH OUT, THIS MIGHT CREATE DUPLICATE LINKED BANKS IF SOME LINKED BANK DATA CHANGES
        # NEED TO SPECIFY EACH KEY FROM PLAID RESPONSE SINCE SOME KEYS ARE NESTED DICTS
        saved_bank_accounts_list = []  # list of bank account objects
        for acct in bank_accounts:
            format_acct_balances = extract_balance_fields_for_plaid_bank_account(acct.pop("balances"))
            filtered_bank_account_data = filter_model_fields(BankAccount, acct)
            filtered_bank_account_data.update(format_acct_balances)
            saved_bank_account, created = BankAccount.objects.get_or_create(
                account_id=filtered_bank_account_data.pop("account_id"),
                linked_bank=saved_linked_bank,
                defaults=filtered_bank_account_data
            )
            saved_bank_accounts_list.append(saved_bank_account)
        linked_bank_serializer = LinkedBankSerializer(saved_linked_bank)
        bank_account_serializer = BankAccountSerializer(saved_bank_accounts_list, many=True)
        # return JsonResponse({"Balance": balance_response.to_dict()}, safe=False)  # prev plaid response
        return JsonResponse({
            "Bank Accounts": bank_account_serializer.data,
            "Linked Bank": linked_bank_serializer.data,
        }, safe=False)
    except plaid.ApiException as e:
        # print(e)  # Uncomment for debugging
        return JsonResponse({"error": str(e)}, status=400)


# This will invalidate the access_token and remove the item from the user's account
# This is a one-way action and cannot be undone
@validate_access_token
def item_remove_request(request, *args, **kwargs):
    try:
        request = ItemRemoveRequest(access_token=kwargs['access_token'])
        response = plaid_client.item_remove(request)
        # The Item was removed and the access_token is now invalid
        return JsonResponse({"success": response.to_dict()})
    except plaid.ApiException as e:
        # print(e)  # Uncomment for debugging
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
        # print(e)  # Uncomment for debugging
        error_response = format_error(e)  # can format other errors this same way later
        return JsonResponse(error_response)


# Get ALL Transactions
# WILL USE THIS ENDPOINT TO CREATE TRANSACTIONS
@validate_access_token
def get_all_transactions(request, *args, **kwargs):
    """
    Get all transactions for the linked bank item,
    then create them internally in subsy.
    """
    # Set cursor to empty to receive all historical updates
    # Provide a cursor from your database if you've previously
    # received one for the Item. Leave null if this is your
    # first sync call for this Item. The first request will
    # return a cursor.
    cursor = ''  # TODO change this to check if non-null cursor exists in company, if so, use existing cursor, else use empty cursor to get all historical transactions

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = []  # Removed transaction ids
    has_more = True
    counter = 1  # for testing
    created_transactions = []  # TODO this is confusing since added included, fix
    try:
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=kwargs.get("access_token"),  # TODO change this to check for company/linked bank access token
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
            # print('MOVING ON TO CURSOR NUMBER:', str(counter))
            # print('has_more equals:', str(has_more))
            # print('LEN OF ADDED TRANSACTIONS:', str(len(added)))
            # print('access token:', kwargs["access_token"])
            # print('='*100)

        # If there's transactions added for linked bank, create transaction objects in subsy db
        if added:
            # TODO perhaps this is NOT THE MOST EFFICIENT, COULD USE BULK OPERATIONS, LOOK INTO IT
            for plaid_transaction in added:
                # filter only required model fields
                plaid_transaction_data = filter_model_fields(Transaction, plaid_transaction)
                # merge the currency fields to get the currency_code
                currency_code = merge_currency_codes(
                    plaid_transaction['iso_currency_code'],
                    plaid_transaction['unofficial_currency_code']
                )
                # add the related bank acct obj to data
                bank_account = BankAccount.objects.get(
                    account_id=plaid_transaction['account_id'],
                )
                plaid_transaction_data['currency_code'] = currency_code
                plaid_transaction_data['bank_account'] = bank_account
                transaction, created = Transaction.objects.get_or_create(
                    transaction_id=plaid_transaction_data.pop('transaction_id'),
                    defaults=plaid_transaction_data,
                )  # TODO when testing this will create error since transaction_id already exists?
                # if transaction was created in subsy, include in created list, else ignore
                if created:
                    created_transactions.append(transaction)
                # TODO since application obj relationship can be null, leave for now, later include application obj logic
            # TODO after adding all new transactions, trigger creating or getting application obj, subscription obj
            # get_or_create_application_obj(created)
        # TODO test that this code works, since don't have modified usually in sandbox or my data
        if modified:
            # will need to fetch transaction, and update only relevant fields
            for plaid_transaction in modified:
                # fetch transaction from db using transaction_id
                try:
                    transaction = Transaction.objects.filter(
                        transaction_id=plaid_transaction['transaction_id']
                    )
                    plaid_transaction_data = filter_model_fields(Transaction, plaid_transaction)
                    # update the new fields for the transaction from plaid
                    transaction.update(**plaid_transaction_data)  # this uses SQL directly, so no need to save
                except ObjectDoesNotExist:
                    print(f'Cannot update. Transaction {plaid_transaction["transaction_id"]} does not exist in db.')

        # If removed do nothing for now
        if removed:
            pass

        # serialize all created transactions
        created_transactions_serializer = TransactionSerializer(
            created_transactions,
            many=True
        )

        all_transactions_response = {
            # TODO change this to return a list of my transaction models, not plaid version
            'added': added,
            'modified': modified,
            'removed': removed,
            'has_more': has_more,
            'cursor': cursor,
            'created': created_transactions_serializer.data,  # for now should return empty list if sandbox and if already have created transactions in db
        }
        return JsonResponse({'all_transactions': all_transactions_response})

    except plaid.ApiException as e:
        # print(e)  # Uncomment for debugging
        error_response = format_error(e)  # can format other errors this same way later
        return JsonResponse(error_response)

def get_or_create_application(created_transactions):
    """Get or create a transaction's application object based on the transaction's merchant name"""
    for transaction in created_transactions:
        # merchant name takes precedence over name
        # if merchant name, check if it already exists in db, else check name exists in db (do nothing)
        merchant_name, name = transaction.merchant_name, transaction.name
        if merchant_name:
            exists = Application.objects.filter(merchant_name__iexact=merchant_name)
        elif name:
            pass

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
