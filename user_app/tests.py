from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

LOGIN_USER_URL = reverse('token_obtain_pair')


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='test', email='test@test.com', password='foo')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email='super@user.com', password='foo')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False)


class BaseTestCase(APITestCase):

    def setUp(self):
        self.username = 'testcase'
        self.email = 'testcase@example.com'
        self.password = 'zaq1@WSX'
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password)
        self.refresh = RefreshToken.for_user(self.user)
        self.data = {
            'email': self.email,
            'password': self.password
        }
        self.client = APIClient(enforce_csrf_checks=True)


class UserAPITests(BaseTestCase):

    def test_jwt_login(self):
        response = self.client.post(LOGIN_USER_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
