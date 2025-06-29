"""
Utils for model-related operations.
"""
import json
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

    return apps_created


def create_or_update_subscriptions(transactions: list):
    """
    Create or update subscriptions for the given transactions.
    :param transactions: List of transaction dicts.
    :return: List of created Subscription objects.
    """

    # Handle empty transactions list
    if not transactions:
        return []

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

    # Get existing subscription app names
    existing_subscription_names = set(existing_subscriptions.values_list("application__name", flat=True)) if existing_subscriptions else set()
    print("existing subscriptions:", existing_subscription_names)

    # Set two lists to create and update subscriptions
    to_create = []
    to_update = []

    acct_application_names = set()

    # For each tx, check if merged_name fn result is in existing_subscription_names, if so, add to_update, else to_create
    for tx in transactions:
        # Get the application name for tx
        app_name = merge_transaction_names(
            tx.get("merchant_name"),
            tx.get("name"),
        )
        acct_application_names.add(app_name)

        # Set the fields needed to update subscription
        sub_fields = {
            "transaction_id": tx.get("id"),
            "application_name": app_name,
        }

        # If app name already exists, add to update list, else to create list
        if app_name in existing_subscription_names:
            to_update.append(sub_fields)
        else:
            to_create.append(sub_fields)

    print("total tx to create subs for:", to_create)
    print("total tx to update subs for:", to_update)

    # Create and update subscriptions from lists

    # Need to pass in Application, Company, and related Transaction. Issue is we need the actual obj instances for each model
    transaction_objs = Transaction.objects.filter(id__in={tx.get("id") for tx in transactions})  # since transactions is a list of dicts, not instances
    application_objs = Application.objects.filter(name__in=acct_application_names)

    # Create lookup dictionaries for efficient access (no repeated DB queries)
    transaction_lookup = {tx.id: tx for tx in transaction_objs}
    application_lookup = {app.name: app for app in application_objs}

    print("company transactions:", len(transaction_objs))
    print("company applications:", len(application_objs))

    # Create Subscription objects efficiently
    created_subscriptions = []

    if to_create:

        to_create_objs = []
        seen_subscriptions = set()

        for tx_data in to_create:
            app_name = tx_data["application_name"]
            transaction_id = tx_data["transaction_id"]

            # Get objects from lookup dictionaries (no DB queries)
            app_obj = application_lookup.get(app_name)
            transaction_obj = transaction_lookup.get(transaction_id)

            # TODO change code to just create subscriptions if sub name not already in app names
            if app_obj and transaction_obj and app_name not in seen_subscriptions:
                sub_obj = Subscription(
                    company=company,
                    application=app_obj,
                )
                seen_subscriptions.add(app_name)
                to_create_objs.append(sub_obj)

        # Bulk create subscriptions
        if to_create_objs:
            created_subscriptions = Subscription.objects.bulk_create(
                to_create_objs,
                batch_size=1000,
            )

            subs_lookup = {sub.application.name: sub for sub in created_subscriptions}

            # Update transactions to link to their subscriptions
            # Since it's one-to-many (Subscription -> Transaction), we update the transaction's subscription field
            for tx_data in to_create:
                tx_id = tx_data["transaction_id"]
                tx_app_name = tx_data["application_name"]
                tx_obj = transaction_lookup.get(tx_id)
                new_sub = subs_lookup.get(tx_app_name)

                if tx_obj and new_sub:
                    tx_obj.subscription = new_sub

            # Bulk update all modified transactions
            if transaction_lookup:
                Transaction.objects.bulk_update(
                    list(transaction_lookup.values()),
                    ['subscription'],
                    batch_size=1000
                )

    if to_update:

        # Need to just add the new transactions to the existing subscriptions
        # Test it out by setting 1 subscription as existing, all new transactions relating to existing subx should be added to that subx
        # to_update["application_name"] contains the app_name
        # Create lookup for existing subscriptions by application name
        existing_subs_lookup = {sub.application.name: sub for sub in existing_subscriptions}

        # Update transactions to link to their existing subscriptions
        for tx_data in to_update:
            tx_id = tx_data["transaction_id"]
            tx_app_name = tx_data["application_name"]
            tx_obj = transaction_lookup.get(tx_id)
            existing_sub = existing_subs_lookup.get(tx_app_name)

            if tx_obj and existing_sub:
                tx_obj.subscription = existing_sub

        # Bulk update all modified transactions for existing subscriptions
        if transaction_lookup:
            Transaction.objects.bulk_update(
                list(transaction_lookup.values()),
                ['subscription'],
                batch_size=1000
            )


    return created_subscriptions


def get_filtered_transactions_for_application_obj(transactions: list):
    """Get filtered transactions for application object creation."""
    # Get only the keys we need for the application object
    # Could later merge merchant_name and name with fn already created in utils.py
    filtered_keys = {"transaction_id", "merchant_name", "name", "website"}  # set for faster lookup performance
    return [{k: tx[k] for k in filtered_keys} for tx in transactions]
