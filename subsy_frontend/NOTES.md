PLAID API REFERENCE
/accounts/balance/get https://plaid.com/docs/api/products/balance/#accountsbalanceget
- returns ITEM/LINKED BANK and a list of all ACCOUNTS
- this endpoint COULD POTENTIALLY HAVE LATENCY, as plaid backend can take 10-30 secs to resolve request, check for that.
- this endpoint better than /accounts/get since fetches latest, not cached, request for all item accounts.

RELEVANT TRANSACTION DATA KEY/VALUE PAIRS
- account_id: bank acct used
- account_owner
- **amount**
- category: similar but not as good as personal_finance_category
- counterparties: could be redundant since most info here also mentioned in outer scope of data, but is a list/dict with data about the merchant like name, logo, website
- **date**
- iso_currency_code (check how this impacts if multi-currency acct)
- **logo_url**
- **merchant_name**: sometimes cleaner than 'name'
- **name**: merchant name
- payment_channel: online vs in-store could be useful
- pending: true or false if payment pending
- **personal_finance_category**: dict with confidence_level, detailed, and primary category info
- **personal_finance_category_icon_url**: like entertainment, food, travel icons
- website

<!--  -->

PLAID SERVER INITIAL TOKEN INTERACTION PROCESS
1. frontend client requests a **link token** to backend python
2. backend python requests a **link token** to plaid
3. plaid sends **link token** to backend python
4. backend python sends **link token** to frontend client
5. frontend client posts **link token** to plaid, which plaid should validate to start Link
6. user signs in through plaid's Link client (their proprietary frontend login client app)
7. plaid sends back a short-lived **public token** to frontend client (lasts 30mins)
8. as soon as frontend client receives the **public token**, it sends it to backend python
9. backend python sends the **public token** to plaid
10. plaid validates **public token**, and sends an access token to backend python
11. access token is stored securely in backend python
