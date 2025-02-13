"""
Tests for models.
"""
from django.test import TestCase  # , Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
# from django.forms.models import model_to_dict

from utils import random_37_char_string
from core.tests.shared_data import (
    create_default_instances,
    TEST_BANK_ACCOUNT_DATA,
    TEST_TRANSACTION_DATA,
)
from core.models import (
    Company,
    LinkedBank,
    BankAccount,
    Transaction,
    # Application,
    # Subscription,
    # Tag,
)


class UserModelTests(TestCase):
    """Test the User model."""

    @classmethod
    def setUpTestData(cls):
        cls.data = create_default_instances()

    # test base success case user created and is active
    def test_create_user_with_email_successful(self):
        """ Test creating a user with an email is successful,
            hashed password is correct, and defaults are set
            correctly.
        """
        email = 'test2@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password), password)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    # email must be normalized
    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        # domains must be lowercase
        sample_emails = [
            ('test1@EXAMPLE.com', 'test1@example.com'),
            ('Test2@Example.com', 'Test2@example.com'),
            ('TEST3@EXAMPLE.com', 'TEST3@example.com'),
            ('test4@example.COM', 'test4@example.com'),
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'testpass123')

            self.assertEqual(user.email, expected)

    # email must be valid
    def test_email_not_valid(self):
        """Test user email input is not valid."""
        sample_bad_emails = [
            '',
            'test_string',
            'test_no_domain@',
            'test_no_at_symbol.com',
            '@test_no_input_before_at.com',
        ]
        for email in sample_bad_emails:
            # user should NOT be created with invalid email
            with self.assertRaises(ValidationError):
                get_user_model().objects.create_user(
                    email=email,
                    password='testpass123'
                )

    # email must be unique
    def test_email_must_be_unique(self):
        """Test that checks if email is unique by creating email duplicate."""
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email='test@example.com',  # this already in setup data
                password='testpass456'
            )

    # optional password
    def test_password_is_optional(self):
        """Test the password is optional field."""
        email = 'test2@example.com'
        password = None
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertFalse(user.check_password(password))

    # minimum password length should be 8 chars
    def test_minimum_password_length(self):
        """Test the minimum password length is 8 chars."""
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email='test2@example.com',
                password='a234567'
            )

    # if super user check True is_active and is_superuser and is_staff
    def test_create_superuser(self):
        """Test creating a superuser is successfull and is_active,
        is_superuser, is_staff all True."""
        user = get_user_model().objects.create_superuser(
            'test2@example.com',
            'testpass123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    # if extra fields passed to create_user, they should be valid though will raise error since User model does not allow for those fields
    def test_user_extra_fields_raise_type_error(self):
        """Test extra fields are accepted as params in UserManager
        but raise type error in user creation model
        (since fields not set in user model)."""
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user(
                email='test2@example.com',
                extra_field_1=500,
                extra_field_2=['a', 'b'],
            )


class CompayModelTests(TestCase):
    """Test the Company model."""

    @classmethod
    def setUpTestData(cls):
        cls.data = create_default_instances()

    company_name = 'test_company'
    company_domain = 'example.com'

    # create company is successful
    def test_create_company_successful(self):
        """Test creating a company is successful."""
        company = Company.objects.create(
            name=self.company_name,
            domain=self.company_domain
        )
        self.assertEqual(company.name, self.company_name)
        self.assertEqual(company.domain, self.company_domain)

    # name must be filled out
    def test_name_not_null(self):
        """Test that name field is not null."""
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name=None,
                domain=self.company_domain,
            )

    # domain must be filled out
    def test_domain_not_null(self):
        """Test the domain field is not null."""
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name=self.company_name,
                domain=None
            )

    # domain must be unique
    def test_domain_is_unique(self):
        """Test the company domain is unique."""
        Company.objects.create(
            name=self.company_name,
            domain=self.company_domain
        )
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name='second company',
                domain=self.company_domain
            )

    # test creating relationship to user is successful
    def test_user_relation_success(self):
        """Test creating a user relation is successful."""
        user = get_user_model().objects.create_user(
            email='test2@example.com',
            password='testpass123'
        )
        company = Company.objects.create(
            name=self.company_name,
            domain=self.company_domain
        )
        company.users.add(user)
        self.assertEqual(company.users.get(pk=user.pk).email, user.email)
        self.assertEqual(user.companies.get(pk=company.pk).pk, company.pk)


class LinkedBankModelTests(TestCase):
    """Test the LinkedBank model."""

    @classmethod
    def setUpTestData(cls):
        cls.data = create_default_instances()

    def setUp(self):
        """Create company for tests."""
        self.company = Company.objects.create(
            name='Apple',
            domain='apple.com'
        )

        # one way to do this is here in setUp, or could use another module
        self.test_dict = {
            'company': self.company,
            'item_id': '3eWb5P7zNlfZABn9yqjos4zK3yvwD4FqwmNNp',
            'institution_id': 'ins_56',
            'institution_name': 'Chase',
        }

    # create LinkedBank is successful
    def test_create_linked_bank_successful(self):
        """Test creating a linked bank account (plaid item)
            is successful.
        """
        linked_bank = LinkedBank.objects.create(**self.test_dict)
        self.assertEqual(linked_bank.company, self.test_dict['company'])
        self.assertEqual(linked_bank.item_id, self.test_dict['item_id'])
        self.assertEqual(linked_bank.institution_id, self.test_dict['institution_id'])
        self.assertEqual(linked_bank.institution_name, self.test_dict['institution_name'])

    # item_id is unique
    def test_linked_bank_item_id_is_unique(self):
        """Test that creating a duplicate item_id raises error."""
        LinkedBank.objects.create(**self.test_dict)
        duplicate_linked_bank = {
            'company': self.company,
            'item_id': '3eWb5P7zNlfZABn9yqjos4zK3yvwD4FqwmNNp',
            'institution_id': 'ins_56',
            'institution_name': 'Chase',
        }
        with self.assertRaises(IntegrityError):
            LinkedBank.objects.create(**duplicate_linked_bank)


    # if company deleted, related linkedbank also deleted
    def test_linked_bank_company_deletion_cascade(self):
        """Test that deleting a linked bank's company also deletes the related linked bank."""
        test_company = Company.objects.create(name='X', domain='x.com')
        linked_bank = LinkedBank.objects.create(**{**self.test_dict, 'company': test_company})

        test_company.delete()

        self.assertFalse(LinkedBank.objects.filter(id=linked_bank.id).count())  # Should be deleted

    # if no company FK, raise error
    def test_linked_bank_no_company_FK_error(self):
        """Test that trying to create a linked bank obj without company returns error."""
        with self.assertRaises(IntegrityError):
            self.test_dict['company'] = None
            LinkedBank.objects.create(**self.test_dict)


class BankAccountTests(TestCase):
    """Test the Bank Account model."""

    @classmethod
    def setUpTestData(cls):
        cls.data = create_default_instances()

    # test bank acct success
    def test_create_bank_account_success(self):
        """Test that creating a bank account is successful."""
        bank_account_data = TEST_BANK_ACCOUNT_DATA.copy()
        account_id = '123ZXwn1mehQnBvRlbtGtJgAD23MkJc4DAwVk'
        bank_account_data['account_id'] = account_id
        bank_account = BankAccount.objects.create(
            **bank_account_data,
            linked_bank=self.data['linked_bank']
        )

        self.assertEqual(bank_account.account_id, account_id)

    # if no linked bank FK, raise error
    def test_create_bank_acct_no_linked_bank_FK_error(self):
        """Test that creating a bank account with no linked bank returns error."""
        with self.assertRaises(IntegrityError):
            bank_account_data = TEST_BANK_ACCOUNT_DATA.copy()
            account_id = '123ZXwn1mehQnBvRlbtGtJgAD23MkJc4DAwVk'
            bank_account_data['account_id'] = account_id
            BankAccount.objects.create(
                **bank_account_data,
                linked_bank=None
            )

    # test deleting a bank acct's linked bank also deletes the bank acct
    def test_deleting_linked_bank_deletes_bank_acct(self):
        """Test that deleting a bank account's linked bank cascades deletion of bank acct."""
        self.data['linked_bank'].delete()  # will only delete for this test, Django refreshes the db setup for each test

        self.assertFalse(BankAccount.objects.filter(id=self.data['bank_account'].id).count())

    # test all fields can be null except account_id, linked_bank
    def test_some_fields_can_be_null(self):
        """Test that all nullable fields can be null."""
        test_bank_account = {}
        for k in TEST_BANK_ACCOUNT_DATA.keys():
            if k != 'account_id':
                test_bank_account[k] = None
            else:
                test_bank_account[k] = 'ABCZXwn1mehQn11Rlb5G7nvADWkMkJc4DAwVk'
        bank_account = BankAccount.objects.create(
            **test_bank_account,
            linked_bank=self.data['linked_bank']
        )

        self.assertIsInstance(bank_account, BankAccount)


class TransactionTests(TestCase):
    """Test the Transaction model."""

    @classmethod
    def setUpTestData(cls):
        cls.data = create_default_instances()

    def setUp(self):
        self.transaction_data = TEST_TRANSACTION_DATA.copy()

    # test transaction created successfully (relation as well)
    def test_create_transaction_success(self):
        """Test that creating a transaction is successful."""
        self.transaction_data['transaction_id'] = random_37_char_string()  # first time using random generator
        transaction = Transaction.objects.create(
            **self.transaction_data,
            bank_account=self.data['bank_account']
        )

        # SHOULD NOT WORK SINCE TRANSACTION W/SAME ID ALREADY EXISTS
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.transaction_id, self.transaction_data.get('transaction_id'))

    # test some values can be null
    def test_null_values_valid_creating_transactions(self):
        """Test that creating transaction with valid null values is successful."""
        # for k/v pair, if k can be null, set to null, else set to something

        for k in self.transaction_data.keys():
            if k == 'transaction_id':
                self.transaction_data[k] = random_37_char_string()
            elif k == 'account_id':
                continue
            else:
                self.transaction_data[k] = None
        transaction = Transaction.objects.create(
            **self.transaction_data,
            bank_account=self.data.get('bank_account')
        )

        self.assertEqual(transaction.account_owner, None)
        self.assertIsInstance(transaction, Transaction)

    # test no FK to bank acct returns error
    def test_no_FK_to_bank_acct_error(self):
        """Test that failing to include a FK to bank acct obj returns error."""
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(
                **self.transaction_data,
                # no bank_account FK
            )

    # test obj deletion if parent obj is deleted

    # APPLICATION

    # SUBSCRIPTION

    # TAG
