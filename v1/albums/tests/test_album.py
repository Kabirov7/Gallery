import json
import io
import shutil
import tempfile

from PIL import Image

from rest_framework import status
from rest_framework.test import APITestCase, APIClient, RequestsClient, override_settings
from rest_framework.reverse import reverse

from v1.accounts.models.user import User
from v1.albums.models.album import Album
from v1.images.models.image import Image as ImageModel

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AlbumTest(APITestCase):

    def setUp(self):
        self.user_data = {
            "email": "test_user@email.com",
            "username": "testinger",
            "password": "12345678!",
            "first_name": "Tester",
            "last_name": "Testerov",
        }
        self.user = User.objects.create(**self.user_data)
        self.user.set_password(self.user_data['password'])
        self.user.save()
        self.client = self.prepare_client(self.user)

    def create_user(self, data=None):
        d = data
        if not d:
            d = self.user_data
        response = self.client.post(
            reverse("registration"), data=d, format="json"
        )
        if response.status_code == status.HTTP_201_CREATED:
            return User.objects.get(
                email=json.loads(response.content)['email'])
        return response

    def prepare_client(self, u):
        client = APIClient()
        client.force_authenticate(u)
        return client

    def generate_photo_file(self, filename=None):
        n = filename
        if not n:
            n = 'test.png'
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = n
        file.seek(0)
        return file

    def test_album_creation(self):
        data = {
            "name": "foo"
        }
        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response ={"path": "foo", "name": "foo"}
        self.assertEqual(json.loads(response.content), expected_response)
        response = self.client.get(reverse('album'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), [expected_response])

    def test_album_duplicate_names(self):
        data = {
            "name": "foo"
        }
        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response ={"path": "foo", "name": "foo"}
        self.assertEqual(json.loads(response.content), expected_response)

        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),
                         {"name": ["Name 'foo' is already taken."]})

    def test_album_invalid_name(self):
        data = {
            "name": "foo////"
        }
        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),
                         {"name": [
                             "Album name can\'t contain \'/\' character"]})

    def test_album_retrieve(self):
        data = {
            "name": "foo boo"
        }
        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)

        url = reverse('album-detail', kwargs={'path': content['name']})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content),
                         {"path": "foo%20boo", "name": "foo boo",
                          "images": []})

    def test_album_retrieve_another_user(self):
        data = {
            "name": "foo boo"
        }
        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_content = json.loads(response.content)

        new_user = self.create_user({
            "email": "new_user@email.com",
            "username": "new123",
            "password": "12345678!",
            "password2": "12345678!",
            "first_name": "new",
            "last_name": "new",
        })
        new_client = self.prepare_client(new_user)
        url = reverse('album-detail', kwargs={'path': response_content['path']})
        response = new_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content),
                         {'detail': 'Not found.'})

    # test create, update, retrieve and delete action on one album.
    def test_album_all_lifecycle(self):
        data = {
            "name": "foo boo"
        }
        response = self.client.post(reverse('album'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content = json.loads(response.content)
        self.assertEqual(content, {'path': 'foo%20boo', 'name': 'foo boo'})

        url = reverse('album-detail',
                      kwargs={'path': data['name']})
        file1 = self.generate_photo_file()
        file2 = self.generate_photo_file()
        file3 = self.generate_photo_file()
        file4 = self.generate_photo_file()
        file1.seek(0)
        file2.seek(0)
        file3.seek(0)
        file4.seek(0)
        to_upload = {
            'file1': file1,
            'file2': file2,
            'file3': file3,
            'file4': file4,
        }
        response = self.client.post(url, to_upload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        uploaded_imgs = json.loads(response.content)['uploaded']
        self.assertEqual(len(uploaded_imgs), 4)
        self.assertEqual(len(json.loads(response.content)['errors']), 0)

        # retrieve updated album
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content)
        for img in uploaded_imgs:
            self.assertIn(img, response_content['images'])

        response = self.client.get(reverse('album'))
        response_content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_content), 1)
        self.assertIn(response_content[0]['image'], uploaded_imgs)


        # test deletion
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.albums.count(), 0)
        self.assertEqual(ImageModel.objects.count(), 0)

    def test_all_albums_deletion(self):
        self.create_user()
        user = User.objects.get(email=self.user_data['email'])
        client = self.prepare_client(user)

        self.assertFalse(user.is_staff)
        data = {
            "name": "foo boo"
        }
        for i in range(7):
            data['name'] += str(i)
            response = client.post(reverse('album'), data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Album.objects.count(), 7)

        # try to delete all
        response = client.delete(reverse('albums-delete-all'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Album.objects.count(), 7)

        user.is_staff = True
        user.save()

        response = client.delete(reverse('albums-delete-all'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Album.objects.count(), 0)
