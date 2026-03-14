from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import UserMetadata


class SignupViewTests(TestCase):
    def test_signup_creates_user_and_metadata(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
                "interests": "gaming",
                "drives": "on",
                "bio": "Test biography.",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="newuser")
        metadata = UserMetadata.objects.get(user=user)

        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(metadata.interests, "gaming")
        self.assertTrue(metadata.drives)
        self.assertEqual(metadata.bio, "Test biography.")

    def test_signup_renders_errors_when_invalid(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "anotheruser",
                "email": "another@example.com",
                "first_name": "Another",
                "last_name": "User",
                "password1": "ComplexPass123",
                "password2": "Mismatch123",
                "interests": "food",
                "bio": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "password fields")
        self.assertFalse(get_user_model().objects.filter(username="anotheruser").exists())
