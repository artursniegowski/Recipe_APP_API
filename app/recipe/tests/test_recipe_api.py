"""
Test for recipe APis.
"""
from core.models import Recipe, Tag, Ingredient
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)
from rest_framework import status
from rest_framework.test import APIClient


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# helper function for creating recipe
def create_recipe(user, **kwargs):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('10.25'),
        'description': 'Sample description',
        'link': 'https://example.com/recipe.pdf',
    }
    # updating the default values
    defaults.update(kwargs)
    # returning the created Reipe object
    return Recipe.objects.create(user=user, **defaults)


def create_user(**kwargs):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**kwargs)


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        # makingsure only authenticated users can retrive recipes
        # getting the recipe url link
        res = self.client.get(RECIPE_URL)
        # making sure the method is not allowed
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        # create a test user
        self.user = create_user(
            email='user@example.com',
            password='testpassword351245',
        )
        # making sure the user is authenticated
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retriving a list of recipes."""

        # creating few test recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        # getting the recipe url link
        res = self.client.get(RECIPE_URL)
        # making sure the recipes are in the respons
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # checking if he order is right - so it has to be descending order
        # newest at the top by id (so the highest id on hte top)
        recipes = Recipe.objects.all().order_by('-id')
        # serializing the retrived objects, this how can we compare
        # that the response from the api is as desired
        serializer = RecipeSerializer(recipes, many=True)

        # data from the response should be equal to serializer data
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""

        # we only want to return recipes for the authenticated user
        # that's currently logged in, so basically only the recipes
        # that belong to the user
        other_user = create_user(
            email='tttester@example.com',
            password='passwordtesaterd3515',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        # getting the recipe url link
        res = self.client.get(RECIPE_URL)
        # making sure the recipes are in the respons
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # getting the recipes for the authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        # serializing the retrived objects
        serializer = RecipeSerializer(recipes, many=True)

        # data from the response should be equal to serialized data
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        # create a random recipe
        recipe = create_recipe(user=self.user)
        # create thedeatil recipe url
        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)

        # making sure the status code respond is ok
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # getting the serialized recipe that we cread before
        # bc it is one recipe we dont have to pass many = True
        serializer = RecipeDetailSerializer(recipe)
        # checkig if data is correct
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe with our API."""

        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('8.25'),
        }
        # passing the payload to the create endpoint
        res = self.client.post(RECIPE_URL, payload)

        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # gettin the recipe by id, it should be created bc we have the status
        # above that indicates success
        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            # here we checking if each element from the payload (keys)
            # is also in the recipe we created and if the values match
            # getting an attribute from an  object
            self.assertEqual(getattr(recipe, k), v)

        # checkingif the user asociated with the recipe is also the user
        # who was authenticated when making the post request
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of recipe"""
        original_link = 'https://example.com/recipe.pdf'
        # creating a new recipe
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        # creating the update payload - only this field should be changed
        payload = {'title': 'New Recipe title'}
        # get the detail url for the recipe
        url = detail_url(recipe.id)
        # getting the respond for a patch request
        res = self.client.patch(url, payload)

        # checking the respond is ok
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh dta from database
        recipe.refresh_from_db()
        # checking if the payload is same as the reponse data
        self.assertEqual(recipe.title, payload['title'])
        # and making sure the other data dint get change
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe"""
        # creating a new recipe
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description',
        )

        # creating the full update payload - everything gets updated
        payload = {
            'title': 'New Recipe title',
            'link': 'https://example2.com/recipe.pdf',
            'description': 'Sample recipe 2 description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        # get the detail url for the recipe
        url = detail_url(recipe.id)
        # getting the respond for the full update
        res = self.client.put(url, payload)

        # checking the respond is ok
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh dta from database
        recipe.refresh_from_db()
        # checking each value from the payload
        # got corectly updated in the recipe
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        # checking that the recipe belongs to the right user
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        # creating a new user
        new_user = create_user(email='new@example.com', password="76i2rfdv32")
        # creating a racipe for the authenticated user
        recipe = create_recipe(user=self.user)

        # trying to updated the user id, this should not work!
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        # the recipe user should not get updated, so shoudl stay the same
        # as it was eventhough we called the patch request
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        # create a sample recipe for test deletion
        recipe = create_recipe(user=self.user)

        # creating the detail url for the recipe
        url = detail_url(recipe.id)
        # sending the deletion request
        res = self.client.delete(url)

        # now we check if the recipe got deleted
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the recipe dosent exists in the database
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        # creating a new user
        new_user = create_user(email='new@example.com', password="76i2rfdv32")
        # creating a racipe for the new_user
        recipe = create_recipe(user=new_user)

        # creating the detail url for the recipe
        url = detail_url(recipe.id)
        # sending the deletion request - this shouldent work
        # bc we are authenticated as self.user and this recipe
        # belong to the new_user
        res = self.client.delete(url)

        # we shuld get an error - page not found
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # the object should still exit
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        # data that will be used to create the recipe with tags
        # so baically the user can asign tags to recipe,
        # and if the tags dont exists they will get created
        # so the url for creating a recipe will also be used
        # for creating tags
        payload = {
            'title': 'Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [
                {'name': 'Thai'},
                {'name': 'Dinner'},
            ]
        }

        # we need to change the format to json bc we are passing
        # nested objects, the tags are nested objects.
        res = self.client.post(RECIPE_URL, payload, format='json')

        # tessting the results of creating the recipes
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        # chekcing if the tags got created properly with the recipe
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        # this test is to make sure that if a tag aleady exists
        # and we create a recipe with taht tag that the tag dosent get
        # created again as this woudl lead to unneccesary duplicates

        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': "Butter Chicken",
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [
                {'name': 'Indian'},  # this exists and should not be added
                {'name': 'Dinner'},
            ]
        }

        # format json as there a nested objects
        # creating the recipe with tags
        res = self.client.post(RECIPE_URL, payload, format='json')

        # evalutaing the results
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        # the indian tag should not be created as it already exists
        # so the indain tag shoudl be asigned to this recipe
        self.assertEqual(recipe.tags.count(), 2)
        # make sure the indian tag is in the tags created by the self.user
        self.assertIn(tag_indian, recipe.tags.all())
        # chekcing if the tags got created properly with the recipe
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag when updating a recipe"""
        # so basically when we update a recipe, and lets say add a tag
        # that wasent there before, then this tag needs to be created as well

        recipe = create_recipe(user=self.user)
        # creaitng the payload to update the tag
        payload = {'tags': [{'name': 'Lunch'}]}
        # creating the url
        url = detail_url(recipe.id)
        # making the request - (partiala updating), updating the tags
        # so this dont change anything else
        res = self.client.patch(url, payload, format='json')

        # chekcing the response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # chekcing the data
        new_tag = Tag.objects.get(
            user=self.user, name=payload['tags'][0]['name']
            )
        # now the above request shoul have updated the recipe by adding the
        # tag in the recipe
        # you dont need to use the db_refresh bc after call recipe.tags.all()
        # we are basically mkaign a new query, and it will do the refresh
        # objects fro this particular recipe
        self.assertIn(new_tag, recipe.tags.all())
        # making sure there are the tags
        self.assertEqual(recipe.tags.count(), 1)

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        # so here we create a recipe with a tag
        tag_bread = Tag.objects.create(user=self.user, name='Bread')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_bread)

        # create a new  objet for testing
        payload = {
            'tags': [
                {'name': 'Lunch'}
            ]
        }
        # and passing the data from the payload to create the object
        tag_lunch = Tag.objects.create(user=self.user, **payload['tags'][0])

        # creating the url
        url = detail_url(recipe.id)
        # making a update request for the tag
        res = self.client.patch(url, payload, format='json')

        # chcking if it was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # chekcing the data
        self.assertIn(tag_lunch, recipe.tags.all())
        # making sure there is only one tag, as the patch request should
        # update the tag value not add a new value
        self.assertNotIn(tag_bread, recipe.tags.all())
        # so we shoudl have only one tag
        # making sure there are the tags
        self.assertEqual(recipe.tags.count(), 1)

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        # clearing all tags asigned to this recipe

        # creating testing data
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        # making the request to clear the tags
        res = self.client.patch(url, payload, format='json')

        # checking the data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_creating_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        # craeting test data
        payload = {
            'title': 'Tacos',
            'time_minutes': 60,
            'price': Decimal('4.30'),
            'ingredients': [
                {'name': 'Tacos'},
                {'name': 'Salt'}
                ],
        }
        # making the request to create the recipe with
        # ingredients
        res = self.client.post(RECIPE_URL, payload, format='json')

        # checking the response data if
        # it is as expected
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingred in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingred['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """test creating a new recipe with existing ingredient."""
        # test ingredient bofore we create a recipe
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        # pyload to craete a recipe
        payload = {
            'title': 'Lemon Soup',
            'time_minutes': 80,
            'price': '2.30',
            'ingredients': [
                {'name': 'Lemon'},
                {'name': 'Salt'}
                ],
        }
        # making the request
        res = self.client.post(RECIPE_URL, payload, format='json')

        # checking the data if it is as expected -
        # leomn shoudlnot be created twice
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingred in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingred['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe."""
        recipe = create_recipe(user=self.user)
        # data for the update
        payload = {
            'ingredients': [
                {'name': 'Limes'}
            ]
        }
        # url for the update
        url = detail_url(recipe.id)

        # making the request
        res = self.client.patch(url, payload, format='json')

        # checking the data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')
        # bc the ingredient donset exists in the database we expect that
        # our patch request would do that
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assing_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        # creating test data
        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Cheese')
        payload = {'ingredients': [{'name': 'Cheese'}]}
        url = detail_url(recipe.id)

        # making the request
        res = self.client.patch(url, payload, format='json')

        # checking if the request yielded data as expected
        # if it updated the recipe as expected
        # so bsically peppershoul change t chili
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        # creating test data
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Garlick',
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        # empty list ofingredients
        payload = {
            'ingredients': []
        }

        url = detail_url(recipe.id)

        # makingthe request
        res = self.client.patch(url, payload, format='json')

        # checkign the response, if it worked as expected
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
