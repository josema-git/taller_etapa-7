from django.urls import reverse
from rest_framework import status
from users.models import User

def test_success_register(client, db):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
    assert User.objects.get().username == 'testuser'
    assert User.objects.get().team == 'default_team'

def test_success_register_empty_team_default(client, db):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
        'team': ''
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
    assert User.objects.get().username == 'testuser'
    assert User.objects.get().team == 'default_team'

def test_failed_register_empty_password(client, db):
    response = client.post(reverse('register'), {
        'username': 'testuser',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 0

def test_failed_register_empty_username(client, db):
    response = client.post(reverse('register'), {
        'password': 'testpassword',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 0

def test_failed_register_existing_username(client, db):
    User.objects.create_user(username='testuser', password='testpassword', team='testgroup')
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 1