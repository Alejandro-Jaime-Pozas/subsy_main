# Overview

App that collects all of your accounts company pays for (g suite, airbyte, stitch, slack, simon, notion, ramp, perkup, figma, etc) and updates realtime which is active, cancelled, cost summary, recommendations, etc.
- You can connect your accounting software like quickbooks, xero, freshbooks, expensify or individually link all of your company bank accounts (PLAID) so we can get all of your subscriptions.

Once we have all of your bank accounts/credit cards/paypal, etc, MySubs will
    - Show all of your active subscriptions in a dashboard for mgmt
        ○ ie: Notion, Slack, G suite, Airbyte, Postgresql, Github, AWS,
    - If click on a specific sub detail,
        ○ get insights into past/future spending patterns and usage to see if worth keeping/dropping/switching to alternative; (if linked to quickbooks can easily track subscription spend vs revenue)
        ○ Details like sub duration, next payment date,
        ○ Link to manage that specific sub
    - track each of the subscriptions you have and check whether it is active or inactive
    - let you know if a subscription is soon expiring or up for renewal
    - let you know if a sub is periodic (contract) or indefinite, meaning it will always charge that card with no set end date (netflix, but not something like airbyte maybe)
      - will be challenge to define if is contract, would need pay history OR api access to platform..
    - Link to each of your subscription websites to manage the subscription if needed (ideally would be able to modify subscription within MySubs)\
      - would need api auth access and require user who signs up to have access to change sub...hard
    - will let you know when a card you use to pay with is EXPIRING
    - Recommend subscriptions using AI search tool where user can specify tool needed, and MySubs finds best subscription deals (think netflix free 2 months, disney plus bundle, partner deals, etc hooked to a 3rd party deals api like couponbirds or something)
      - Subsy could potentially partner w/apps for deals, but always be impartial in terms of best recommendations
    - Marketplace of possible subscriptions to benefit the company (with recommendation system)
    - Deals deals deals. New bank acct deals, subscription deals, etc (could partner/integrate/link to nerd wallet or partner directly w/providers)

## FRONTEND

    MAIN MENU
        - MAIN DASHBOARD
            § Obj: user to have an eagle eye view of all of their subscription spend
        - HISTORICAL/FORECASTS
            § Obj: show user how each sub relates to each other in terms of cost to ease their decisions to renew or cancel or change providers
            § Would imagine chart with all subs through time, could filter by spend amount per month/yr or by category, etc
            § If quickbooks integrated, could provide views of sub spend vs revenue or something
        - APP MARKETPLACE
            § Obj: user can search for apps by name but more so by use or function (ie app that helps get more linkedin inbound leads; app that takes data from different sources and connects to snowflake; app to visualize snowflake data and creates reports)
            § Use prompt that would fetch openAI or some AI's backend and retrieve the best apps. ie for data ETL tool: fivetran, airbyte, stitch.
        - RECOMMENDED APPS (will be part of app marketplace if there is no search by user yet)
            § Based on current subs, suggest apps that could benefit them THAT USER DOESN'T KNOW ABOUT (would be most beneficial to cofounders, CTOs, managers/execs but not admin)
            § Could also provide alternative apps for current subscriptions that cost less or have great deals (if user looking to save on costs)
        - LINKED BANK ACCOUNTS
            § Show bank accounts and credit cards linked to acct. can manage them from here
            § Could also show subs filtered by acct here, or could be a filter in main dashboard

    MAIN DASHBOARD

    Options for columns:
        ○ Cost per month
        ○ Period ie mthly, yrly
        ○ Whether it's a fixed amount or varies per month usage
        ○ Last payment date
        ○ Next payment date
        ○ Contract expiry date (so they can assess whether to keep sub or not)
        ○ Last 3/6/12 months cost
        ○ Active/inactive (will need to access sub APIs..)
        ○ How many months sub has been paid
        ○ Which depts within company use this sub
            § Ie: all, admin, ops, sales, marketing, etc
        ○ Linked bank acct/card: ie chase credit, chase checking, discover CD, capital one savings ,etc
            § Bank logo would be ideal
        ○ Sub purpose: ie marketing automation, communication, data storage, analysis
        ○ Sub manager: ie the person who is in charge of the sub, maybe not paying it but determining its usefulness or champion user


    Detail view:
        ○ This could expand when you click on the sub in main dashboard, or could be separate page (expand best)
        ○ All details in columns should be included
        ○ Also perhaps include chart of historical payments, how it compares to total expenses or something

    *Very important to have VISUAL components where it helps the user out most. So, for example, each sub company logo; to identify transaction/sub types: admin, hr, tech, auomtation, collab, marketing, etc. Also for the bank accounts the bank logo
    *This is PRIMARILY an intuitive app for frontend use, not like AWS or something much more technical, this is a basic use app (but where's the value if very low user interaction?).


## BACKEND

## Database

### Overview

URL relationship diagram: https://lucid.app/lucidchart/09f82465-b143-4aa5-ae47-e29c728e4c5c/edit?viewport_loc=-2398%2C-2540%2C3206%2C1144%2C0_0&invitationId=inv_fc19301a-e399-41a6-8355-1f9ccf2add46


At the top level really is the company object. A company is always linked to a user, as is a user always linked to a company (though user can have personal email in which case their company will be their unique email).
  - The company name will be extracted using the user's work (or personal) email domain via the hunter.io API https://hunter.io/api-documentation/v2


A company can also have a LinkedBank. LinkedBank refers to the user-specific log in to their online bank provider (ie Chase online bank).A linked bank, as opposed to just a bank, refers to a company user's link to their online bank. This is different from just referring to a bank, where Chase has millions of clients which would be considered a bank.
  - PLAID USES AN OBJ CALLED ITEM which includes the user's online bank provider details as well as all of the bank accts for that user's online bank. ITEM REFERENCES A USER'S LOGIN CREDENTIALS (not a single login) TO AN ONLINE BANK. SO, ITEM = LINKED BANK. THE ONLY ISSUE THAT COULD ARISE IS IF USER CHANGES THEIR LOGIN CREDENTIALS, THEN WILL RETURN ERROR AND WILL NEED TO PROMPT USER TO UPDATE THAT (read plaid docs for this).
  - PLAID API will be used to integrate a user's online bank into our API
  - PLAID API REFERENCE
  - /accounts/balance/get https://plaid.com/docs/api/products/balance/#accountsbalanceget
    - returns ITEM/LINKED BANK and a list of all ACCOUNTS
    - this endpoint COULD POTENTIALLY HAVE LATENCY, as plaid backend can take 10-30 secs to resolve request, check for that.
    - this endpoint better than /accounts/get since fetches latest, not cached, request for all item accounts.




So a linked bank is a user-specific log in to their online bank, which can have multiple bank accounts. a bank acct could be for example a 'savings', 'checking', 'cd', '401k' or other account. A bank account should be unique and have an account number and routing number in most cases.


A bank account then can have transactions within it. Each transaction is specific to a unique bank account. A transaction is any monetary value exchange between the user's bank account and any other entity.


A transaction then can **possibly** indicate there's an application involved. An application can have multiple transactions (suppose a user subscribes to Netflix, the user will have multiple monthly transactions for 1 subscription, Netflix in this case) within the same company or between different companies since **applications are globally scoped**.


An application exists outside of our django app universe (in a sense) and does not need to be linked to a subscription. Applications are the equivalent of a software platform like Notion, Slack, etc. They exist outside the scope of our universe. A subscription is always linked to an application.
  - To implement application creation, could either find an existing API that somehow contains most online subscription platforms, or could create the application when considering a transaction that is referencing an application that does not yet exist in our django app universe. Example, django app has Snowflake and Azure as apps only, a new transaction comes in from user bank that is AWS, so AWS is checked in db, and created since it did not exist.


A subscription is for the purposes of our specific django app universe, a software platform of some form that the company subscribes to in a given, **uninterrupted** time period. It is not the application itself, it is a set of details usually including a payment for the services of that application in a given time period. If a subscription is cancelled and then resumed, it will still NOT count as the same subscription. Bill payments for utilities are NOT a subscription. Payment to a supplier is NOT a subscription. A subscription is an online software platform like Notion, Slack, Google Suite, AWS, Snowflake, Sales Nav, etc that is utilized within the company.
  - WILL USE ANNOTATE() CAPABILITY TO CREATE AGGREGATIONS REQUIRED TO ANALYZE SPEND AND SHOW TO USER IN FRONTEND
    - ChatGPT response: Use an annotate() QuerySet for On-the-Fly Aggregation



A subscription then can also have tags for different purposes, such as what specific company dept the sub belongs to. A tag can exist on its own (to have a set of default tags), or it can be linked to a sub. There could be different types of tags, should outline this better.


A subscription can also be linked to a sub manager, which is the user managing that specific subscription. This user can either be active or passive within the platform, but they essentially (but not directly within the app), dictate whether the subscription should be modified in any way perhaps.

### Data Architecture

    - COMPANY > USER
        ○ MANY TO MANY
        ○ MAIN = COMPANY
        ○ User must have at least one company (if no company default to user email for company name.)
        ○ Company must have at least one user
    - COMPANY > LINKED BANK
        ○ ONE TO MANY
        ○ MAIN = COMPANY
        ○ A company can have 0 or many linked banks
        ○ A linked bank must have at least 1 company, at most one company
    - LINKED BANK > BANK ACCOUNT
        ○ ONE TO MANY
        ○ MAIN = LINKED BANK
        ○ Linked bank  can have 0 or many bank accts
        ○ A bank acct must have one bank
    - BANK ACCOUNT > TRANSACTION
        ○ ONE TO MANY
        ○ MAIN = BANK ACCOUNT
        ○ A bank acct can have 0 or many transactions
        ○ A transaction must have one bank acct
    - TRANSACTION > APPLICATION
        ○ ONE TO MANY
        ○ MAIN = APPLICATION
        ○ A transaction can have 0 or 1 application
        ○ An application can have 0 or many transactions
    - SUBSCRIPTION > APPLICATION
        ○ ONE TO MANY
        ○ MAIN = APPLICATION
        ○ A subscription must have 1 application
        ○ An application can have 0 or many subscriptions (since apps exist outside of mysubs universe)
    - SUBSCRIPTION > TAG
        ○ MANY TO MANY
        ○ MAIN = SUBSCRIPTION
        ○ A subsription can have 0 or many tags
        ○ A tag can have 0 or many subscriptions
    - SUBSCRIPTION > USER
        - MANY TO MANY
        - MAIN = USER
        - a subscription can have 0 or many users (subscription_manager)
        - a user can have 0 or many subscriptions for which they're in charge
