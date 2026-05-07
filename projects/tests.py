from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


class ProjectViewsTests(TestCase):
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
        self.project = Project.objects.create(
            name="Test project",
            description="Test description",
            owner=self.user,
            status=Project.STATUS_OPEN,
        )

    def test_projects_list_page_opens(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test project")

    def test_project_detail_page_opens(self):
        response = self.client.get(reverse("projects:detail", args=[self.project.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test project")

    def test_create_project_requires_login(self):
        response = self.client.get(reverse("projects:create"))

        self.assertEqual(response.status_code, 302)

    def test_logged_user_can_create_project(self):
        self.client.login(email="user@example.com", password="password")

        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "New project",
                "description": "New description",
                "github_url": "https://github.com/test/project",
                "status": Project.STATUS_OPEN,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name="New project").exists())

    def test_owner_can_complete_project(self):
        self.client.login(email="user@example.com", password="password")

        response = self.client.post(
            reverse("projects:complete", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_user_can_toggle_favorite(self):
        self.client.login(email="other@example.com", password="password")

        response = self.client.post(
            reverse("projects:toggle_favorite", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.other_user.favorites.filter(pk=self.project.pk).exists())

    def test_user_can_toggle_participation(self):
        self.client.login(email="other@example.com", password="password")

        response = self.client.post(
            reverse("projects:toggle_participate", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.project.participants.filter(pk=self.other_user.pk).exists()
        )
