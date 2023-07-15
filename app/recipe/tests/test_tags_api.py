"""
Tests for the tags API.
"""
from core.models import Recipe, Tag
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='test[ass123]'):
    """Create adn return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        # checking if we get acces denied when user  not authenticated
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retrieving a list of tags."""
        # creating some sample tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # checkign the response
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # checking if the data is the same
        # we specify theorder bc by using different version
        # of the default databse we might have different order
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        # runnign the test if the data is as expected
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        # creating anotheruser for test
        user2 = create_user(email='user22@exampl.com')
        # creating tags with different users
        Tag.objects.create(user=user2, name='Mains')
        tag = Tag.objects.create(user=self.user, name="Ice cream")

        # checking the response
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # checking the data
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        # creating a new tag
        tag = Tag.objects.create(user=self.user, name="Default tag")

        # values for the update
        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)

        # making the request to update
        res = self.client.patch(url, payload)

        # checking if it worked
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # updating the value of the database tag
        tag.refresh_from_db()
        # ceckingactualy the data
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        # checkingif it worked
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to thoes assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_minutes=10,
            price=Decimal('2.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        # making the request with the params
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # checking data
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=100,
            price=Decimal('6.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Pallela',
            time_minutes=50,
            price=Decimal('16.50'),
            user=self.user,
        )
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        # making the request with the params
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # checking data
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
