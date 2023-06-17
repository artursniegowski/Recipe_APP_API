"""
Test for the Django admin modifications.
"""

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Djagno admin."""

    def setUp(self) -> None:
        """Create user and client."""

        self.client = Client()
        # login as admin
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="test12414ds;gjfhoa;hou",
        )
        self.client.force_login(self.admin_user)
        # create a regular user in the database
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="test1fafaffhoa;hou",
            name="Test User",
        )

    def test_users_list(self):
        """Test that users are listed on page."""

        # https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
        # #reversing-admin-urls
        # this will be the url for the change list inside the
        # django admin
        # this will be the list of users
        # we are authenticated as admin user so we shell be able to view it
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        # we checkif the actual user exists in the list
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works"""

        # geting the specific user page
        url = reverse("admin:core_user_change", args=(self.user.id,))
        res = self.client.get(url)
        # makign sure the page responds with 200 - status OK
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works"""

        # geting the specific user page - link for adding a user
        # no id needed since we try to create a new user
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        # makign sure the page responds with 200 - status OK
        self.assertEqual(res.status_code, 200)
