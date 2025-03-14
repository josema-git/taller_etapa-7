from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from users.models import User

# Create your tests here.
class BloggerRegisterCase(TestCase):
    def test_success_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'testpassword',
            'group_name': 'testgroup'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertEqual(User.objects.get().groups.all()[0].name, 'testgroup')

    def test_success_register_empty_group_name_default(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'testpassword',
            'group_name': ''
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertEqual(User.objects.get().groups.all()[0].name, 'default_group')

    def test_failed_register_empty_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': '',
            'group_name': 'testgroup'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_failed_register_empty_username(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'password': 'testpassword',
            'group_name': 'testgroup'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_failed_register_existing_username(self):
        User.objects.create_user(username='testuser', password='testpassword', group_name='testgroup')
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'testpassword',
            'group_name': 'testgroup'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

class BloggerLoginCase(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', password='testpassword', group_name='testgroup')
    
    def test_success_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_failed_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_failed_login_nonexistent_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistentuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BloggerLogoutCase(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', password='testpassword', group_name='testgroup')

    def test_success_logout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_failed_logout_unauthenticated(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    

