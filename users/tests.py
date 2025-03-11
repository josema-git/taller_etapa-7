from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User, Group

# Create your tests here.
class BloggerRegisterCase(TestCase):
    def test_succesful_register(self):
        response = self.client.post(reverse('register-list'), {
            'username': 'testuser',
            'password': 'testpassword',
            'groups': 'testgroup'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertEqual(User.objects.get().groups[0].name, 'testgroup')

    def test_failed_register(self):
        response = self.client.post(reverse('register-list'), {
            'username': 'testuser',
            'password': 'testpassword',
            'groups': 'testgroup'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)