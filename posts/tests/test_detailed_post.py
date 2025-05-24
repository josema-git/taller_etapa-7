import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post
from rest_framework.test import APIClient

@pytest.fixture
def setup_posts(client):
    user = User.objects.create_user(username='poster', password='testpassword', team='testgroup1')
    
    user = User.objects.get(username='poster')
    
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, team='testgroup1',
        authenticated_permission=1, group_permission=1, author_permission=2, author=user
    )
    authenticated_post = Post.objects.create(
        title='authenticatedpost', content='authenticatedcontent', is_public=0, team='testgroup1',
        authenticated_permission=1, group_permission=1, author_permission=2, author=user
    )
    group_post = Post.objects.create(
        title='grouppost', content='groupcontent', is_public=0, team='testgroup1',
        authenticated_permission=0, group_permission=1, author_permission=2, author=user
    )
    private_post = Post.objects.create(
        title='privatepost', content='privatecontent', is_public=0, team='testgroup1',
        authenticated_permission=0, group_permission=0, author_permission=2, author=user
    )
    
    return {
        'user': user,
        'public_post': public_post,
        'authenticated_post': authenticated_post,
        'group_post': group_post,
        'private_post': private_post
    }

def test_read_everything_as_author_or_superuser(db, setup_posts):
    client = APIClient()

    client.force_authenticate(user=setup_posts['user'])
    
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.get(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'publicpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'authenticatedpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'grouppost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'privatepost'
    
    client.post(reverse('logout'))

def test_read_public_authenticated_and_group_posts(db, setup_posts):
    client = APIClient()
    user = User.objects.create_user(username='reader', password='testpassword', team='testgroup1')
    client.force_authenticate(user=user)
    
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.get(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'publicpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'authenticatedpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'grouppost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    client.post(reverse('logout'))

def test_read_public_and_authenticated_posts(db, setup_posts):
    client = APIClient()
    user = User.objects.create_user(username='reader', password='testpassword', team='testgroup2')
    client.force_authenticate(user=user)
    
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.get(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'publicpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'authenticatedpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response = client.get(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    client.post(reverse('logout'))

def test_read_public_posts(client ,db, setup_posts):
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.get(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'publicpost'
    
    response = client.get(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response = client.get(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response = client.get(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND