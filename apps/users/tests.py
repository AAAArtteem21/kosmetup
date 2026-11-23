from django.contrib import admin
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .admin import ClientAdmin
from .models import Client


class AuthenticationTests(APITestCase):
    password = "Strong-Password-932!xyz"

    def test_registration_creates_user_and_returns_tokens(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-client",
                "email": "new-client@example.com",
                "password": self.password,
                "first_name": "New",
                "last_name": "Client",
                "is_staff": True,
                "role": Client.Role.COSMETOLOGIST,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotIn("password", response.data["user"])
        user = Client.objects.get(username="new-client")
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.role, Client.Role.CLIENT)
        self.assertFalse(user.is_staff)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-client",
                "email": "new-client@example.com",
                "password": "password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Client.objects.filter(username="new-client").exists())

    def test_token_authenticates_me_endpoint(self):
        user = Client.objects.create_user(
            username="existing-client",
            email="existing-client@example.com",
            password=self.password,
        )
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": self.password},
            format="json",
        )

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(user.id))

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_client_is_registered_with_user_admin(self):
        self.assertIsInstance(admin.site._registry[Client], ClientAdmin)
