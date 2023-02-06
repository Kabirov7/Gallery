import json
import tempfile

from rest_framework import status
from rest_framework.test import (
    APITestCase, APIClient, RequestsClient, override_settings
)
from rest_framework.reverse import reverse

from v1.accounts.models.user import User


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RegistrationTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test_user@email.com",
            "username": "testinger",
            "password": "12345678!",
            "password2": "12345678!",
            "first_name": "Tester",
            "last_name": "Testerov",
        }
        self.client = APIClient()
        pass

    def create_user(self, data=None):
        d = data
        if not d:
            d = self.user_data
        response = self.client.post(
            reverse("registration"), data=self.user_data, format="json"
        )
        return response

    def test_user_registration_and_login(self):
        response = self.create_user()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_data = self.user_data.copy()
        del expected_data["password"]
        del expected_data["password2"]
        self.assertEqual(json.loads(response.content), expected_data)
        self.assertEqual(User.objects.count(), 1)

    def test_login_exist_user(self):
        user = self.create_user()
        self.assertEqual(User.objects.count(), 1)

        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        response = self.client.post(reverse("login"), data=login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(json.loads(response.content)["token"])
        self.assertEqual(json.loads(response.content)["email"],
                         self.user_data["email"])

    def test_duplicate_mail(self):
        response = self.create_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.create_user()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = self.user_data.copy()
        data["username"] += "d"
        response = self.create_user(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),
                         {"username": [
                             "A user with that username already exists."],
                          "email": ["This field must be unique."]})

    def test_incorrect_password(self):
        response = self.create_user()
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]+"!INCORRECT_PASS!"
        }
        response = self.client.post(reverse("login"), data=login_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNotNone(json.loads(response.content)["detail"],
                             "Password is incorrect.")

    def test_user_doesnt_exist(self):
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]+"!INCORRECT_PASS!"
        }
        response = self.client.post(reverse("login"), data=login_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(json.loads(response.content)["detail"],
                             "Not found.")

    def test_user_full_info(self):
        self.create_user()
        user = User.objects.get(email='test_user@email.com')
        self.client.force_authenticate(user)

        response = self.client.get(reverse('profile'))
        content = json.loads(response.content)
        del content['id']
        del content['date_joined']
        user_data = {"username": "testinger", "first_name": "Tester",
         "last_name": "Testerov", "email": "test_user@email.com"}
        self.assertEqual(content, user_data)


