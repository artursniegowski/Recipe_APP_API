"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    """Create and return a newuser."""
    return get_user_model().objects.create_user(**kwargs)


# tests broken into two categories
# where users need to be authenticated and where they dont
# like users dont need to be authenticated to register user
class PublicUserApiTest(TestCase):
    """Test the public features of the user API.
    Users dont need to be authenticated."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'asdfghjkl;weq',
            'name': 'Test Name',
        }
        # post request to the create url
        res = self.client.post(CREATE_USER_URL, payload)

        # checking for the right status code in response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # getting the user from the database
        user = get_user_model().objects.get(email=payload['email'])
        # checking if the password still matches
        self.assertTrue(user.check_password(payload['password']))
        # checking that the hash password is not returned in the respond
        # if it was than it is a security issue!
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'asdfghjkl;weq',
            'name': 'Test Name',
        }
        # first create a user witht he given payload in the databse
        create_user(**payload)
        # post request to the create url - try to create user that already
        # exists - this sould return an error
        res = self.client.post(CREATE_USER_URL, payload)
        # and checking if we get a bad request response from the API
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        # try to create a user with the too short password
        res = self.client.post(CREATE_USER_URL, payload)
        # this should lead to an error respond from the API
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # make sure the user was not created
        user_exists = get_user_model().objects.filter(
            email=payload['email'],
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'tesfdasghq893p8hcn4943du',
        }
        # creating auser withthe given credentials
        create_user(**user_details)

        # for the token creation
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        # creating the token, it should return a response
        # with the token for the user, this has to be used for authentication
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_bad_credentails(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='fgakslbvealendw')

        payload = {
            'email': 'test@example.com',
            'password': 'badpassword',
        }
        # making a request with bad credentials, wrong password
        res = self.client.post(TOKEN_URL, payload)
        # making sure that the request failed
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        # making a post request with blank password
        res = self.client.post(TOKEN_URL, payload)
        # this should also fail
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test authentication is required for uesrs."""
        # we are making unathenticated request to the endpoint
        res = self.client.get(ME_URL)
        # this should return an unauthorized error
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# test for users with valid tokens
class PrivateUserApiTest(TestCase):
    """Test the private features of the user API.
    Users need to be authenticated """

    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            password='sdekraguiewhgfreah',
            name='test name',
        )
        self.client = APIClient()
        # so any request made from this point on will be
        # made by a user that is authenticated
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retriving profile for logged in user."""
        res = self.client.get(ME_URL)
        # so we are checkingif the respond had the correct data,
        # since the user is authenticated it should return
        # name and email
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})
        # since a post method is not allowed to the ME_URL
        # this shoudl return an error
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name': 'Updated Name', 'password': 'newpassword12412'}
        # now making a patch request to update the data
        res = self.client.patch(ME_URL, payload)
        # making sure we will get the updated data from the database
        self.user.refresh_from_db()
        # checkignfi the user data was updated
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
