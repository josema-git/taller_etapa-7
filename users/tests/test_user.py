import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User

# Fixtures
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username='testuser', password='testpassword', team='testgroup'
    )

# === Autenticación: Login ===

@pytest.mark.django_db
def test_success_login(api_client, test_user):
    url = reverse('token_obtain_pair')
    resp = api_client.post(url, {'username': 'testuser', 'password': 'testpassword'})
    assert resp.status_code == status.HTTP_200_OK
    assert 'access' in resp.data and 'refresh' in resp.data

@pytest.mark.django_db
def test_failed_login_wrong_password(api_client, test_user):
    url = reverse('token_obtain_pair')
    resp = api_client.post(url, {'username': 'testuser', 'password': 'wrong'})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_failed_login_nonexistent_user(api_client):
    url = reverse('token_obtain_pair')
    resp = api_client.post(url, {'username': 'no', 'password': 'no'})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

# === Autenticación: Refresh  ===

@pytest.mark.django_db
def test_success_token_refresh(api_client, test_user):
    tokens = api_client.post(reverse('token_obtain_pair'), {'username': 'testuser', 'password': 'testpassword'}).data
    resp = api_client.post(reverse('token_refresh'), {'refresh': tokens['refresh']})
    assert resp.status_code == status.HTTP_200_OK
    assert 'access' in resp.data

@pytest.mark.django_db
def test_failed_token_refresh_invalid(api_client):
    resp = api_client.post(reverse('token_refresh'), {'refresh': 'invalid'})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

# === Autenticación: Logout ===

@pytest.mark.django_db
def test_success_logout(api_client, test_user):
    tokens = api_client.post(reverse('token_obtain_pair'), {'username': 'testuser', 'password': 'testpassword'}).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    resp = api_client.post(reverse('logout'), {'refresh': tokens['refresh']})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['message'] == 'Logout successful'

@pytest.mark.django_db
def test_failed_logout_missing_refresh(api_client, test_user):
    tokens = api_client.post(reverse('token_obtain_pair'), {'username': 'testuser', 'password': 'testpassword'}).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    resp = api_client.post(reverse('logout'), {})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data['message'] == 'Refresh token is required'

@pytest.mark.django_db
def test_failed_logout_invalid_refresh(api_client, test_user):
    tokens = api_client.post(reverse('token_obtain_pair'), {'username': 'testuser', 'password': 'testpassword'}).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    resp = api_client.post(reverse('logout'), {'refresh': 'wrongtoken'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data['message'] == 'Invalid token'

@pytest.mark.django_db
def test_failed_logout_unauthenticated(api_client):
    resp = api_client.post(reverse('logout'), {'refresh': 'no'})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

# === Registro de Usuarios ===

@pytest.mark.django_db
def test_success_register_default_team(api_client):
    resp = api_client.post(reverse('register'), {'username': 'new', 'password': 'pass'})
    assert resp.status_code == status.HTTP_201_CREATED
    u = User.objects.get(username='new')
    assert u.team == 'default_team'

@pytest.mark.django_db
def test_success_register_empty_team(api_client):
    resp = api_client.post(reverse('register'), {'username': 'new2', 'password': 'pass', 'team': ''})
    assert resp.status_code == status.HTTP_201_CREATED
    u = User.objects.get(username='new2')
    assert u.team == 'default_team'

@pytest.mark.django_db
def test_failed_register_missing_username(api_client):
    resp = api_client.post(reverse('register'), {'password': 'pass'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_failed_register_missing_password(api_client):
    resp = api_client.post(reverse('register'), {'username': 'new'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_failed_register_existing_username(api_client, test_user):
    resp = api_client.post(reverse('register'), {'username': 'testuser', 'password': 'testpassword'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

# === Perfil de Usuario ===

@pytest.mark.django_db
def test_profile_requires_authentication(api_client):
    resp = api_client.get(reverse('user'))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_profile_retrieval(api_client, test_user):
    tokens = api_client.post(reverse('token_obtain_pair'), {'username': 'testuser', 'password': 'testpassword'}).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    resp = api_client.get(reverse('user'))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {'username': 'testuser'}
