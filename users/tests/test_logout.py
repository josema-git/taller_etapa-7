import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User

@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpassword', team='testgroup')

@pytest.mark.django_db
def test_success_logout(client, test_user):
    token = client.post(reverse('token_obtain_pair'), {
        'username': 'testuser',
        'password': 'testpassword'
    }).data

    
    response = client.post(reverse('logout'), {
        'refresh': token['refresh']
    }, HTTP_AUTHORIZATION=f'Bearer {token["access"]}')

    print(response.data)
    
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_failed_logout_unauthenticated(client):
    response = client.post(reverse('logout'))
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED