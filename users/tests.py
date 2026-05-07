from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project
from users.forms import ProfileForm
from users.models import User


class UserViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com",
            password="password",
            name="User",
            surname="Test",
            phone="+79990000001",
        )

    def test_register_page_opens(self):
        response = self.client.get(reverse("users:register"))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_page_opens(self):
        response = self.client.get(reverse("users:login"))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_list_page_opens(self):
        response = self.client.get(reverse("users:list"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "User")

    def test_user_detail_page_opens(self):
        response = self.client.get(reverse("users:detail", args=[self.user.pk]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "User")

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse("users:edit_profile"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_change_password_requires_login(self):
        response = self.client.get(reverse("users:change_password"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class ProfileFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com",
            password="password",
            name="User",
            surname="Test",
            phone="+79990000001",
        )
        cls.other_user = User.objects.create_user(
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
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="password",
            name="Owner",
            surname="Test",
            phone="+79990000001",
        )
        cls.viewer = User.objects.create_user(
            email="viewer@example.com",
            password="password",
            name="Viewer",
            surname="Test",
            phone="+79990000002",
        )
        cls.project = Project.objects.create(
            name="Owner project",
            description="Description",
            owner=cls.owner,
        )
        cls.viewer.favorites.add(cls.project)

    def setUp(self):
        self.viewer_client = Client()
        self.viewer_client.force_login(self.viewer)

    def test_favorite_authors_filter(self):
        response = self.viewer_client.get(
            reverse("users:list"),
            {"filter": "owners-of-favorite-projects"},
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Owner")
