"""
Tests for the ingredients API.
"""
from core.models import Ingredient, Recipe
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from recipe.serializers import IngredientSerializer
from rest_framework import status
from rest_framework.test import APIClient


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth isrequired for retriving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        # checking if the respond is corect
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        """Test retriving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Curry')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        # checking the respond
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # checking the data
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authneticate user."""
        # createing test data with unauthenticated user
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name="Pepper")
        # creating test data with authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')

        # getting the respond
        res = self.client.get(INGREDIENTS_URL)

        # checking the response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Curry'
        )
        # uploading the data
        payload = {
            'name': 'Coriander'
        }
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        # checking if the response was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh the database to get the updated data
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        # create test data
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Lettuce'
        )
        # sending the delete url
        url = detail_url(ingredient.id)
        # making the req
        res = self.client.delete(url)

        # checking if it worked
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # checking if the data is gone
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by thoes assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Bananas')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        # making the request with a parameter
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        # checking data
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')

        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=50,
            price=Decimal('7.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('3.50'),
            user=self.user,
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        # making the request
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        # checking data
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
