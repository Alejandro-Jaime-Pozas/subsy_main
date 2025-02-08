"""
Tests for models.
"""
from django.test import TestCase  # , Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
# from django.forms.models import model_to_dict

from core.tests.shared_data import create_default_instances
from core.models import (
    Company,
    LinkedBank,
    BankAccount,
    # Transaction,
    # Application,
    # Subscription,
    # Tag,
)


class UserModelTests(TestCase):
    """Test the User model."""

    # @classmethod
    # def setUpTestData(cls):
    #     cls.data = create_default_instances()

    # test base success case user created and is active
    def test_create_user_with_email_successful(self):
        """ Test creating a user with an email is successful,
            hashed password is correct, and defaults are set
            correctly.
        """
        email = 'test@example.com'
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
        get_user_model().objects.create_user(
            email='test@example.com',
            password='nomatter'
        )
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email='test@example.com',
                password='testpass456'
            )

    # optional password
    def test_password_is_optional(self):
        """Test the password is optional field."""
        email = 'test@example.com'
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
                email='test@example.com',
                password='a234567'
            )

    # if super user check True is_active and is_superuser and is_staff
    def test_create_superuser(self):
        """Test creating a superuser is successfull and is_active,
        is_superuser, is_staff all True."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
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
                email='test@example.com',
                extra_field_1=500,
                extra_field_2=['a', 'b'],
            )


class CompayModelTests(TestCase):
    """Test the Company model."""

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
            email='test@example.com',
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


# class BankAccountTests(TestCase):
#     """Test the Bank Account model."""

#     def setUp(self):
#         # create a test bank acct
#         self.setup_bank_account = BankAccount.objects.create(**setup_bank_account_dict)

#     # test bank acct success
#     def test_create_bank_account_success(self):
#         """Test that creating a bank account is successful."""
#         bank_account = BankAccount.objects.create(**bank_account_dict)
#         print(bank_account.__dict__)

#         # self.assertIsInstance(bank_account, BankAccount)
#         self.assertEqual(bank_account.account_id, bank_account_dict['account_id'])

    # test deleting a bank acct's linked bank also deletes the bank acct



    # TRANSACTION

    # APPLICATION

    # SUBSCRIPTION

    # TAG
