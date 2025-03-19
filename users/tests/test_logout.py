import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User

@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpassword', group_name='testgroup')

@pytest.mark.django_db
def test_success_logout(client, test_user):
    client.login(username='testuser', password='testpassword')
    
    response = client.post(reverse('logout'))
    
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_failed_logout_unauthenticated(client):
    response = client.post(reverse('logout'))
    
    assert response.status_code == status.HTTP_403_FORBIDDEN