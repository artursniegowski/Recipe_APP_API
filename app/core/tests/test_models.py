"""
Test for models from the core application.
"""
from core import models
from decimal import Decimal
# helper function to get the default User model for the project
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase


def create_user(email='user@example.com', password='testpassword'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        """Test creating a recipe is successful"""

        # creating a user that will create a recipe
        user = self.User.objects.create_user(
            email='test@example.com',
            password='asdfghjklqwe1341',
            name='test user',
        )
        # creating a recipe
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),  # best practice to store prices is int
            description="Sample recipe description",
        )

        # checking if the recipe was created corectly
        # and if the string representaion is same as the title
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        # creating a tag
        tag = models.Tag.objects.create(
            user=user,
            name='Tag1'
        )

        # checking  if the model was actually created
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient_1'
        )
        # check if the ingredient got created
        self.assertEqual(str(ingredient), ingredient.name)
