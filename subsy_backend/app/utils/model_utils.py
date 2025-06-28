"""
Utils for model-related operations.
"""
from core.models import (
    Application,
    Subscription,
    Company,
    Transaction,
)
from core.tests.shared_data import create_subscription
from utils.utils import merge_transaction_names


# TODO need to add the transaction_id to link the application to specific transaction...or maybe change relationship so tx > sbx > apx?
def create_application_if_not_exists(transactions: list):
    """
    Create Application objects for transactions whose application_name does not exist in the DB.
    Includes both name and website fields. Uses the first website found for each unique application_name.
    :param transactions: List of transaction dicts with application_name and website fields.
    :return: List of created Application objects.
    """

    # 1. Map application_name to website from transactions (first occurrence wins)
    app_name_to_website = {}
    for tx in transactions:
        app_name = merge_transaction_names(
            tx.get("merchant_name"),
            tx.get("name"),
        )  # choose the best name for app
        website = tx.get("website")
        if app_name and app_name not in app_name_to_website:
            app_name_to_website[app_name] = website  # maybe change this later if more fields needed (related_names)

    # 2. Query all existing application names in one DB hit
    existing_apps = set(Application.objects.filter(name__in=app_name_to_website.keys()).values_list("name", flat=True))

    # 3. Find which names need to be created
    to_create = [name for name in app_name_to_website if name not in existing_apps]

    # 4. Bulk create only the missing ones, including website
    apps_created = Application.objects.bulk_create(
        [Application(name=name, website=app_name_to_website[name]) for name in to_create],
        ignore_conflicts=True
    )

    # Get the newly created applications from the db
    created_apps_list = list(Application.objects.filter(
        name__in=[app.name for app in apps_created]
    ))

    return created_apps_list


def create_or_update_subscriptions(transactions: list):
    """
    Create or update subscriptions for the given transactions.
    :param transactions: List of transaction dicts.
    :return: List of created Subscription objects.
    """

    # Handle empty transactions list
    if not transactions:
        return []

    # Set two lists to create and update subscriptions
    to_create = []
    to_update = []

    # Fetch all existing subscriptions in db for the current company
    # Easy way (but not ideal, ideally through user auth or something) to just get company via link trail
    # TODO later change the company get to simpler code using the user's company or something to retrieve
    company = Company.objects.get(
        linked_banks__bank_accounts__id=transactions[0]["bank_account"]
    )
    # # TODO REMOVE THIS ONLY FOR TESTING !!!!
    # test_create_subx = create_subscription(
    #     application=Application.objects.first(),
    # )
    # company.subscriptions.add(test_create_subx)
    # # TODO REMOVE THIS ONLY FOR TESTING !!!!

    existing_subscriptions = company.subscriptions

    # Get the subscription app name
    existing_subscription_names = set(existing_subscriptions.values_list("application__name", flat=True)) if existing_subscriptions else set()
    print(existing_subscription_names)

    # for each tx, check if merged_name fn result is in existing_subscription_names, if so, add to_update, else to_create
    for tx in transactions:
        pass 


def get_filtered_transactions_for_application_obj(transactions: list):
    """Get filtered transactions for application object creation."""
    # Get only the keys we need for the application object
    # Could later merge merchant_name and name with fn already created in utils.py
    filtered_keys = {"transaction_id", "merchant_name", "name", "website"}  # set for faster lookup performance
    return [{k: tx[k] for k in filtered_keys} for tx in transactions]
