from django.urls import reverse
from rest_framework import status
from users.models import User

def test_success_register(client, db):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
        'group_name': 'testgroup'
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
    assert User.objects.get().username == 'testuser'
    assert User.objects.get().groups.first().name == 'testgroup'

def test_success_register_empty_group_name_default(client, db):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
        'group_name': ''
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
    assert User.objects.get().username == 'testuser'
    assert User.objects.get().groups.first().name == 'default_group'

def test_failed_register_empty_password(client, db):
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': '',
        'group_name': 'testgroup'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 0

def test_failed_register_empty_username(client, db):
    response = client.post(reverse('register'), {
        'username': '',
        'password': 'testpassword',
        'group_name': 'testgroup'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 0

def test_failed_register_existing_username(client, db):
    User.objects.create_user(username='testuser', password='testpassword', group_name='testgroup')
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
        'group_name': 'testgroup'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 1