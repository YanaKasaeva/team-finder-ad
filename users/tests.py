from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.forms import ProfileForm
from users.models import User


class UserViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password",
            name="User",
            surname="Test",
            phone="+79990000001",
        )

    def test_register_page_opens(self):
        response = self.client.get(reverse("users:register"))

        self.assertEqual(response.status_code, 200)

    def test_login_page_opens(self):
        response = self.client.get(reverse("users:login"))

        self.assertEqual(response.status_code, 200)

    def test_users_list_page_opens(self):
        response = self.client.get(reverse("users:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User")

    def test_user_detail_page_opens(self):
        response = self.client.get(reverse("users:detail", args=[self.user.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User")

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse("users:edit_profile"))

        self.assertEqual(response.status_code, 302)

    def test_change_password_requires_login(self):
        response = self.client.get(reverse("users:change_password"))

        self.assertEqual(response.status_code, 302)


class ProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password",
            name="User",
            surname="Test",
            phone="+79990000001",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password",
            name="Other",
            surname="Test",
            phone="+79990000002",
        )

    def test_valid_phone_format(self):
        form = ProfileForm(
            data={
                "name": "User",
                "surname": "Test",
                "about": "",
                "phone": "89990000003",
                "github_url": "https://github.com/test",
            },
            instance=self.user,
        )

        self.assertTrue(form.is_valid())

    def test_invalid_phone_format(self):
        form = ProfileForm(
            data={
                "name": "User",
                "surname": "Test",
                "about": "",
                "phone": "123",
                "github_url": "https://github.com/test",
            },
            instance=self.user,
        )

        self.assertFalse(form.is_valid())

    def test_duplicate_phone_is_invalid(self):
        form = ProfileForm(
            data={
                "name": "User",
                "surname": "Test",
                "about": "",
                "phone": "+79990000002",
                "github_url": "https://github.com/test",
            },
            instance=self.user,
        )

        self.assertFalse(form.is_valid())

    def test_non_github_url_is_invalid(self):
        form = ProfileForm(
            data={
                "name": "User",
                "surname": "Test",
                "about": "",
                "phone": "+79990000003",
                "github_url": "https://gitlab.com/test",
            },
            instance=self.user,
        )

        self.assertFalse(form.is_valid())


class UserFilterTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="password",
            name="Owner",
            surname="Test",
            phone="+79990000001",
        )
        self.viewer = User.objects.create_user(
            email="viewer@example.com",
            password="password",
            name="Viewer",
            surname="Test",
            phone="+79990000002",
        )
        self.project = Project.objects.create(
            name="Owner project",
            description="Description",
            owner=self.owner,
        )

    def test_favorite_authors_filter(self):
        self.viewer.favorites.add(self.project)
        self.client.login(email="viewer@example.com", password="password")

        response = self.client.get(
            reverse("users:list"),
            {"filter": "owners-of-favorite-projects"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owner")
