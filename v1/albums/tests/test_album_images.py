import json
import io
import tempfile

from PIL import Image

from rest_framework import status
from rest_framework.test import (
    APITestCase, APIClient, RequestsClient, override_settings
)
from rest_framework.reverse import reverse

from v1.accounts.models.user import User
from v1.albums.models.album import Album
from v1.images.models.image import Image as ImageModel


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AlbumImageDetailTest(APITestCase):
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
        album_data = {"name": "foo"}
        self.client.post(reverse('album'), data=album_data)
        self.album = Album.objects.get(user=self.user,
                                       name=album_data['name'])

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

    def add_image(self, album):
        file = self.generate_photo_file()
        file.seek(0)
        upload = {'file': file}
        url = reverse('album-detail',
                      kwargs={'path': album.name}
                      )
        response = self.client.post(url, upload)
        return response

    def test_image_detail_view(self):
        response = self.add_image(self.album)
        self.assertEqual(Album.objects.count(), 1)
        self.assertEqual(ImageModel.objects.count(), 1)
        img_uploaded = json.loads(response.content)['uploaded'][0]

        url = reverse('album-img-detail', kwargs={
            "album_path": self.album.name,
            "img_path": img_uploaded['path']

        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_answer = {
            'path': img_uploaded['path'],
            'fullpath': img_uploaded['fullpath'],
            'name': img_uploaded['name'],
            'modified': img_uploaded['modified'],
        }
        self.assertEqual(json.loads(response.content), expected_answer)

    def test_image_delete(self):
        response = self.add_image(self.album)
        self.assertEqual(Album.objects.count(), 1)
        self.assertEqual(ImageModel.objects.count(), 1)
        img_uploaded = json.loads(response.content)['uploaded'][0]

        url = reverse('album-img-detail', kwargs={
            "album_path": self.album.name,
            "img_path": img_uploaded['path']

        })
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ImageModel.objects.count(), 0)