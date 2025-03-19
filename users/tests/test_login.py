import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User

@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpassword', group_name='testgroup')

def test_success_login(client, db,test_user):
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'testpassword'
    })
    
    assert response.status_code == status.HTTP_200_OK

def test_failed_login(client, db,test_user):
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_failed_login_nonexistent_user(client, db):
    response = client.post(reverse('login'), {
        'username': 'nonexistentuser',
        'password': 'testpassword'
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST