import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post
from rest_framework.test import APIClient

@pytest.fixture
def setup_posts():
    poster = User.objects.create_user(username='poster', password='testpassword', team='testgroup1')
    Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, team='testgroup1',
        authenticated_permission=1, group_permission=1, author_permission=2, author=poster
    )
    Post.objects.create(
        title='authenticatedpost', content='authenticatedcontent', is_public=0, team='testgroup1',
        authenticated_permission=1, group_permission=1, author_permission=2, author=poster
    )
    Post.objects.create(
        title='grouppost', content='groupcontent', is_public=0, team='testgroup1',
        authenticated_permission=0, group_permission=1, author_permission=2, author=poster
    )
    Post.objects.create(
        title='privatepost', content='privatecontent', is_public=0, team='testgroup1',
        authenticated_permission=0, group_permission=0, author_permission=2, author=poster
    )
    return poster

def test_read_everything_as_author_or_superuser(db, setup_posts):
    client = APIClient()
    client.force_authenticate(user=setup_posts)
    
    response = client.get(reverse('posts'))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 4
    assert response.data['results'][0]['title'] == 'privatepost'
    assert response.data['results'][1]['title'] == 'grouppost'
    assert response.data['results'][2]['title'] == 'authenticatedpost'
    assert response.data['results'][3]['title'] == 'publicpost'
    
    client.post(reverse('logout'))

def test_read_public_authenticated_and_group_posts(db, setup_posts):
    client = APIClient()
    reader = User.objects.create_user(username='reader', password='testpassword', team='testgroup1')
    client.force_authenticate(user=reader)
    
    response = client.get(reverse('posts'))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    assert response.data['results'][0]['title'] == 'grouppost'
    assert response.data['results'][1]['title'] == 'authenticatedpost'
    assert response.data['results'][2]['title'] == 'publicpost'
    
    client.post(reverse('logout'))

def test_read_public_and_authenticated_posts(db, setup_posts):
    client = APIClient()
    reader = User.objects.create_user(username='reader', password='testpassword', team='testgroup2')
    client.force_authenticate(user=reader)
    
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

