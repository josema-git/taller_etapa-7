import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post

@pytest.fixture
def setup_posts(client):
    client.post(reverse('register'), {
        'username': 'poster',
        'password': 'testpassword',
        'group_name': 'testgroup1'
    })
    
    user = User.objects.get(username='poster')
    
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
        authenticated_permission=1, group_permission=1, author_permission=2, author=user
    )
    authenticated_post = Post.objects.create(
        title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
        authenticated_permission=1, group_permission=1, author_permission=2, author=user
    )
    group_post = Post.objects.create(
        title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
        authenticated_permission=0, group_permission=1, author_permission=2, author=user
    )
    private_post = Post.objects.create(
        title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
        authenticated_permission=0, group_permission=0, author_permission=2, author=user
    )
    
    return {
        'user': user,
        'public_post': public_post,
        'authenticated_post': authenticated_post,
        'group_post': group_post,
        'private_post': private_post
    }

def test_read_everything_as_author_or_superuser(client, db, setup_posts):
    client.post(reverse('login'), {
        'username': 'poster',
        'password': 'testpassword'
    })
    
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

def test_read_public_posts(client, db, setup_posts):
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