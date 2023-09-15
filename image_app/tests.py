import io
from PIL import Image as img

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken

from user_app.models import AccountTier
from .models import Image

UPLOAD_IMAGE_URL = reverse('image_create')
LIST_IMAGE_URL = reverse('image_list')


def generate_photo_file():
    file = io.BytesIO()
    image = img.new('RGBA', size=(100, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    uploaded_file = InMemoryUploadedFile(file, None, 'test.png', 'image/png', file.tell(), None)
    return uploaded_file


class ImageUploadViewTest(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.basic = AccountTier.objects.create(name='Basic',
                                                thumbnail_size='200',
                                                original_link=False,
                                                expiring_link=False
                                                )
        self.premium = AccountTier.objects.create(name='Premium',
                                                  thumbnail_size='200,400',
                                                  original_link=True,
                                                  expiring_link=False
                                                  )
        self.enterprise = AccountTier.objects.create(name='Enterprise',
                                                     thumbnail_size='200,400',
                                                     original_link=True,
                                                     expiring_link=True
                                                     )

        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='foo',
                                             account_tier=self.basic)
        self.refresh = RefreshToken.for_user(self.user)
        self.client = APIClient(enforce_csrf_checks=True)

    def test_image_upload_valid_file(self):
        self.client.force_authenticate(user=self.user)
        photo_file = generate_photo_file()
        data = {
            "original_image": photo_file
        }
        response = self.client.post(UPLOAD_IMAGE_URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Image.objects.filter(user=self.user).exists())
        self.assertTrue(len(response.data['thumbnails']), 1)
        self.assertNotIn('original_link', response.data)

    def test_image_upload_invalid_file(self):
        self.client.force_authenticate(user=self.user)
        invalid_file_content = b"not_an_image_content"
        invalid_file = SimpleUploadedFile("test.txt", invalid_file_content, content_type="text/plain")
        data = {'original_image': invalid_file}
        response = self.client.post(UPLOAD_IMAGE_URL, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Image.objects.filter(user=self.user).exists())

    def test_image_upload_no_file(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(UPLOAD_IMAGE_URL, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_upload_unauthorized(self):
        response = self.client.post(UPLOAD_IMAGE_URL, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        for image in Image.objects.all():
            if image.original_image:
                image.original_image.delete(save=False)
        Image.objects.all().delete()

    def test_image_upload_basic_tier(self):
        self.client.force_authenticate(user=self.user)
        photo_file = generate_photo_file()
        data = {
            "original_image": photo_file
        }
        response = self.client.post(UPLOAD_IMAGE_URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Image.objects.filter(user=self.user).exists())
        self.assertTrue(len(response.data['thumbnails']), 1)
        self.assertNotIn('original_link', response.data)

    def test_image_upload_premium_tier(self):
        self.user.account_tier = self.premium
        self.client.force_authenticate(user=self.user)
        photo_file = generate_photo_file()
        data = {
            "original_image": photo_file
        }
        response = self.client.post(UPLOAD_IMAGE_URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Image.objects.filter(user=self.user).exists())
        self.assertTrue(len(response.data['thumbnails']), 2)
        self.assertTrue('original_link', response.data)

    def test_image_upload_enterprise_tier(self):
        self.user.account_tier = self.enterprise
        self.client.force_authenticate(user=self.user)
        photo_file = generate_photo_file()
        data = {
            "original_image": photo_file
        }
        response = self.client.post(UPLOAD_IMAGE_URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Image.objects.filter(user=self.user).exists())
        self.assertTrue(len(response.data['thumbnails']), 2)
        self.assertTrue('original_link', response.data)


class ImageListViewTest(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.basic = AccountTier.objects.create(name='Basic',
                                                thumbnail_size='200',
                                                original_link=False,
                                                expiring_link=False
                                                )
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='foo',
                                             account_tier=self.basic
                                             )
        photo_file = generate_photo_file()
        Image.objects.create(user=self.user, original_image=photo_file)
        self.refresh = RefreshToken.for_user(self.user)
        self.client = APIClient(enforce_csrf_checks=True)

    def test_image_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(LIST_IMAGE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_image_list_unauthenticated(self):
        self.client.logout()
        response = self.client.get(LIST_IMAGE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
