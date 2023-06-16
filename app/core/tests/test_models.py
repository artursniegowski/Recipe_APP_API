"""
Test for models from the core application.
"""
# helper function to get the default User model for the project
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase


class ModelTests(TestCase):
    """Test models."""

    def setUp(self) -> None:
        self.User = get_user_model()

    def test_create_user_with_email_successful(self) -> None:
        """Test creating a regular user with an email is successful."""

        email = 'test@example.com'
        password = 'test123pass!@#'

        user = self.User.objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_super_user_with_email_successful(self) -> None:
        """Test creating a super user with an email is successful."""

        email = 'test_super@example.com'
        password = 'test_super123pass!@#'

        user = self.User.objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_email_unique(self) -> None:
        """Test checking of the uniqunes of the eamil address is enforced"""

        with self.assertRaises(IntegrityError):
            # this has to throw an error, bc we cant have two
            # same email addresses
            email = "tester@example.com"
            password = "123asfassg34t52"

            self.User.objects.create_user(
                email=email,
                password=password
            )
            self.User.objects.create_user(
                email=email,
                password=password
            )

    def test_new_user_without_email_error(self):
        """Test checking that user creation without an email will raise Value
        Error"""

        email = ""
        password = "123asfassg34t52"

        with self.assertRaises(ValueError):
            # this has to throw an error bc email is not defined
            self.User.objects.create_user(
                email=email,
                password=password
            )

    def test_email_validation(self) -> None:
        """Test checking if the email is validated proeprly"""

        with self.assertRaises(ValidationError):
            email = 'invalid_email'
            password = 'test_super123pass!@#'

            user = self.User(
                email=email,
                password=password,
            )
            user.full_clean()
            user.save()

    def test_new_user_email_normalized(self) -> None:
        """Test email is normalized for new users"""
        # [email_before_normalized, email_after_normalized]
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        # exctracting elemnts
        for email, expected in sample_emails:
            user = self.User.objects.create_user(
                email=email,
                password='samlfjdafhasjdfh1231',
            )
            self.assertEqual(user.email, expected)
