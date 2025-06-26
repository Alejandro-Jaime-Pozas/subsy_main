"""
Utils for model-related operations.
"""


def create_application_if_not_exists(transactions: list):
    """
    Create an application if it does not already exist based on the transactions provided.
    :param transactions: Dictionary containing transaction data.
    :return: 
    """
    # Check each transaction, create an application if merchant name not in applications
    # create new list of filtered transactions, only need transaction_id, merchant_name (or name), website for now
    filtered_keys = {"transaction_id", "merchant_name", "website"}
    transactions = []


def update_or_create_subscription(transactions: dict):
    pass 
