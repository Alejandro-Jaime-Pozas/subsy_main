"""
Utils for model-related operations.
"""
from utils.utils import merge_transaction_names


def create_application_if_not_exists(transactions: list):
    """
    Create an application if it does not already exist based on the transactions provided.
    :param transactions: Dictionary containing transaction data.
    :return: 
    """
    # # Create new list of filtered transactions, only need transaction_id, merchant_name (or name), website for now
    # filtered_txs = get_filtered_transactions_for_application_obj(transactions)

    # Choose the best name for the application (merchant_name or name) include for each transaction
    transactions_w_app_name = set_application_name(transactions)  # returns addtl application_name field for each tx

    # Check each transaction, create an application if application_name not in applications
    


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
            tx.get("name")
        )
    return transactions


def get_filtered_transactions_for_application_obj(transactions: list):
    """Get filtered transactions for application object creation."""
    # Get only the keys we need for the application object
    # Could later merge merchant_name and name with fn already created in utils.py
    filtered_keys = {"transaction_id", "merchant_name", "name", "website"}  # set for faster lookup performance
    return [{k: tx[k] for k in filtered_keys} for tx in transactions]