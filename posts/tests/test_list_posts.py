import pytest
from django.urls import reverse
from rest_framework import status

@pytest.fixture
def setup_posts(client):
    client.post(reverse('register'), {
        'username': 'poster',
        'password': 'testpassword',
        'group_name': 'testgroup1'
    })
    client.post(reverse('login'), {
        'username': 'poster',
        'password': 'testpassword'
    })
    client.post(reverse('posts'), {
        'title': 'publicpost',
        'content': 'publiccontent',
        'is_public': 1,
        'authenticated_permission': 1,
        'group_permission': 1,
        'author_permission': 2
    })
    client.post(reverse('posts'), {
        'title': 'authenticatedpost',
        'content': 'authenticatedcontent',
        'is_public': 0,
        'authenticated_permission': 1,
        'group_permission': 1,
        'author_permission': 2
    })
    client.post(reverse('posts'), {
        'title': 'grouppost',
        'content': 'groupcontent',
        'is_public': 0,
        'authenticated_permission': 0,
        'group_permission': 1,
        'author_permission': 2
    })
    client.post(reverse('posts'), {
        'title': 'privatepost',
        'content': 'privatecontent',
        'is_public': 0,
        'authenticated_permission': 0,
        'group_permission': 0,
        'author_permission': 2
    })
    client.post(reverse('logout'))

def test_read_everything_as_author_or_superuser(client, db, setup_posts):
    client.post(reverse('login'), {
        'username': 'poster',
        'password': 'testpassword'
    })
    
    response = client.get(reverse('posts'))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 4
    assert response.data['results'][0]['title'] == 'privatepost'
    assert response.data['results'][1]['title'] == 'grouppost'
    assert response.data['results'][2]['title'] == 'authenticatedpost'
    assert response.data['results'][3]['title'] == 'publicpost'
    
    client.post(reverse('logout'))

def test_read_public_authenticated_and_group_posts(client, db, setup_posts):
    client.post(reverse('register'), {
        'username': 'reader',
        'password': 'testpassword',
        'group_name': 'testgroup1'
    })
    client.post(reverse('login'), {
        'username': 'reader',
        'password': 'testpassword'
    })
    
    response = client.get(reverse('posts'))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    assert response.data['results'][0]['title'] == 'grouppost'
    assert response.data['results'][1]['title'] == 'authenticatedpost'
    assert response.data['results'][2]['title'] == 'publicpost'
    
    client.post(reverse('logout'))

def test_read_public_and_authenticated_posts(client, db, setup_posts):
    client.post(reverse('register'), {
        'username': 'reader',
        'password': 'testpassword',
        'group_name': 'testgroup2'
    })
    client.post(reverse('login'), {
        'username': 'reader',
        'password': 'testpassword'
    })
    
    response = client.get(reverse('posts'))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
    assert response.data['results'][0]['title'] == 'authenticatedpost'
    assert response.data['results'][1]['title'] == 'publicpost'

    client.post(reverse('logout'))

def test_read_public_posts(client, db, setup_posts):
    response = client.get(reverse('posts'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'publicpost'

