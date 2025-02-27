"""
Database models.
"""
from django.db import models
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from utils import (
    SUBSCRIPTION_PAYMENT_PERIOD_CHOICES,
    SUBSCRIPTION_PAYMENT_TYPE_CHOICES,
)


class UserManager(BaseUserManager):
    """Manager for User."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        validate_email(email)
        if password:
            validate_password(password)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)  # this supports adding multiple dbs if needed (best practice)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create, save and return a new superuser."""
        superuser = self.create_user(email, password, **extra_fields)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)  # self._db is a BaseManager variable

        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    """User in the db system."""
    email = models.EmailField(max_length=255, unique=True, blank=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # django built-in; should not be in serializer
    is_staff = models.BooleanField(default=False)  # django built-in; should not be in serializer

    objects = UserManager()  # This assigns UserManager to manage the User model, providing methods to create users and superusers.

    USERNAME_FIELD = 'email'  # This sets the field used for authentication to be the email address instead of the default username.

    def __repr__(self) -> str:
        return f'<User {self.id}|{self.email}>'


class Company(models.Model):
    # TODO
    # - create the name field based on the domain name from the user's email using hunter.io API;
    # - maybe add more fields included from hunter.io API when integrating? like company sector/description?
    """Company in the db system. Different companies could have
    the same name but different domains."""
    name = models.CharField(max_length=255, blank=False)  # in theory this should not allow blank strings as input IN FORMS only, but does allow blanks if input directly into model instance
    domain = models.CharField(max_length=255, blank=False, unique=True)
    users = models.ManyToManyField(User, related_name='companies')

    def __repr__(self) -> str:
        return f'<Company {self.id}|{self.name}|{self.domain}>'


class LinkedBank(models.Model):
    """Linked Bank (equivalent to Plaid Item) in the db system."""
    item_id = models.CharField(max_length=37, unique=True)  # Plaid Item is a user's login credentials to a specific bank, like Chase. Unique !!!BE AWARE THAT MULTIPLE USERS LINKING THE SAME ONLINE BANK COULD RESULT IN DUPLICATE LINKEDBANKS FOR THE SAME COMPANY!!!
    institution_id = models.CharField(max_length=25, )  # Plaid id for the bank. Not unique
    institution_name = models.CharField(max_length=55, )  # Plaid name for the bank. Not unique
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='linked_banks')

    def __repr__(self):
        return f'<LinkedBank {self.id}|{self.institution_name}|{self.institution_id}>'


class BankAccount(models.Model):
    """Bank account in the db system."""
    account_id = models.CharField(max_length=37, unique=True)
    balances_available = models.IntegerField(null=True)
    balances_current = models.IntegerField(null=True)
    balances_limit = models.IntegerField(null=True)
    balances_currency_code = models.CharField(max_length=10, null=True)  # will merge iso_currency_code with unofficial_currency_code when request comes in
    name = models.CharField(max_length=255, null=True)
    official_name = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=25, null=True)
    subtype = models.CharField(max_length=50, null=True)
    linked_bank = models.ForeignKey(LinkedBank, on_delete=models.CASCADE, related_name='bank_accounts')

    def __repr__(self):
        return f'<BankAccount {self.id}|{self.name}|{self.subtype}|{self.account_id}>'


class Application(models.Model):
    """
    Software application/platform in the db system.
    i.e. Snowflake, Azure, AWS are applications.
    """
    name = models.CharField(max_length=255, unique=True)  # assumed by the transaction merchant data
    website = models.URLField(max_length=5000, null=True)  # from transaction website field
    manage_subscription_link = models.URLField(max_length=5000, default=None, null=True)  # will later need to find best way to automate finding subscription page links for all applications..

    def __repr__(self):
        return f'<Application {self.id}|{self.name}>'


class Transaction(models.Model):
    """Transaction (cash in or cash out) in the db system."""
    transaction_id = models.CharField(max_length=37, unique=True)
    account_id = models.CharField(max_length=37)
    account_owner = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    counterparties = models.JSONField(null=True)
    datetime = models.DateTimeField(null=True)
    currency_code = models.CharField(max_length=10, null=True)  # will merge iso_currency_code with unofficial_currency_code when request comes in
    logo_url = models.URLField(max_length=1000, null=True)
    merchant_name = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    payment_channel = models.CharField(max_length=255, null=True)
    pending = models.BooleanField(null=True)
    personal_finance_category = models.JSONField(null=True)
    personal_finance_category_icon_url = models.URLField(max_length=1000, null=True)
    website = models.URLField(max_length=1000, null=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, related_name='transactions', null=True)

    def __repr__(self):
        return f'<Transaction {self.id}|{self.merchant_name}|{self.name}|{self.transaction_id}>'


class Subscription(models.Model):
    """
    Subscription in the db system. A subscription is a software platform
    of some form that the company subscribes to in a given, possibly
    interrupted time period.
    """

    start_date = models.DateTimeField(default=None, null=True)
    end_date = models.DateTimeField(default=None, null=True)
    active = models.BooleanField(default=True)
    payment_period = models.CharField(
        default='Monthly',
        choices=SUBSCRIPTION_PAYMENT_PERIOD_CHOICES,
        null=True
    )
    payment_type = models.CharField(
        default='Variable',
        choices=SUBSCRIPTION_PAYMENT_TYPE_CHOICES,
        null=True
    )
    last_payment_date = models.DateTimeField(default=None, null=True)
    next_payment_date = models.DateTimeField(default=None, null=True)
    application = models.ForeignKey(
        Application,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )  # models.PROTECT to prevent deletion of application since would delete all related subscriptions
    subscription_manager = models.ForeignKey(  # maybe naming convention not smartest since it differs
        User,
        on_delete=models.SET_NULL,
        related_name='subscriptions',
        null=True
    )

    def __repr__(self):
        return f'<Subscription {self.id}|{self.application.name}|{self.start_date}>'


class Tag(models.Model):
    """
    Tag in the db system. Multi-purpose tag for use in grouping/filtering.
    Can extend to other objects besides Subscription.
    """
    name = models.CharField(max_length=50)
    subscriptions = models.ManyToManyField(Subscription, related_name='tags')

    def __repr__(self):
        return (
            f'<Tag {self.id}|{self.name}|'
            f'subscriptions count: {len(self.subscriptions.all())}>'
        )
