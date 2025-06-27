"""
Utils for model-related operations.
"""
from core.models import Application
from utils.utils import merge_transaction_names


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


def update_or_create_subscription(transactions: dict):
    pass


def set_application_name(transactions: list):
    """
    Set the name for the application based on the
    transaction merchant_name vs name.
    """
    for tx in transactions:
        tx["application_name"] = merge_transaction_names(
            tx.get("merchant_name"),
            tx.get("name"),
        )
    return transactions


def get_filtered_transactions_for_application_obj(transactions: list):
    """Get filtered transactions for application object creation."""
    # Get only the keys we need for the application object
    # Could later merge merchant_name and name with fn already created in utils.py
    filtered_keys = {"transaction_id", "merchant_name", "name", "website"}  # set for faster lookup performance
    return [{k: tx[k] for k in filtered_keys} for tx in transactions]
