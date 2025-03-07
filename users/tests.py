from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from django.contrib.auth.models import User, Group
from .models import Blogger

# Create your tests here.
class BloggerRegisterCase(TestCase):
    def test_blogger_register_succesful(self):
        response = self.client.post(reverse('register'), {'username': 'test_user_succesful', 'password': 'test_password_succesful'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_blogger_register_fail_duplicated_user(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        response = self.client.post(reverse('register'), {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blogger_register_fail_empty_username(self):
        response = self.client.post(reverse('register'), {'username': '', 'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_blogger_register_fail_empty_password(self):
        response = self.client.post(reverse('register'), {'username': 'test_user', 'password': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    
class BloggerLoginCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.team = Group.objects.create(name='test_team')
        self.blogger = Blogger.objects.create(user=self.user, team=self.team)

    def test_blogger_login(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blogger_login_fail_wrong_password(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_blogger_login_fail_wrong_username(self):
        response = self.client.post(reverse('login'), {'username': 'wrong_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blogger_login_fail_empty_username(self):
        response = self.client.post(reverse('login'), {'username': '', 'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blogger_login_fail_empty_password(self):
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BloggerLogoutCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.team = Group.objects.create(name='test_team')
        self.blogger = Blogger.objects.create(user=self.user, team=self.team)

    def test_blogger_logout(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blogger_logout_fail_not_logged_in(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)