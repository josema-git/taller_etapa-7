import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Like
from rest_framework.test import APIClient

@pytest.fixture
def create_user_and_posts():
    user = User.objects.create_user(username='poster', password='testpassword', team='testgroup1')
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, team='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=user
    )
    authenticated_post = Post.objects.create(
        title='authenticatedpost', content='authenticatedcontent', is_public=0, team='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=user
    )
    group_post = Post.objects.create(
        title='grouppost', content='groupcontent', is_public=0, team='testgroup1',
        authenticated_permission=0, group_permission=2, author_permission=2, author=user
    )
    private_post = Post.objects.create(
        title='privatepost', content='privatecontent', is_public=0, team='testgroup1',
        authenticated_permission=0, group_permission=0, author_permission=2, author=user
    )

    return {
        "user": user,
        "public_post": public_post,
        "authenticated_post": authenticated_post,
        "group_post": group_post,
        "private_post": private_post,
    }

def test_like_everything_as_author_or_superuser(db, create_user_and_posts):
    client = APIClient()
    public_post = create_user_and_posts['public_post']
    authenticated_post = create_user_and_posts['authenticated_post']
    group_post = create_user_and_posts['group_post']
    private_post = create_user_and_posts['private_post']

    client.force_authenticate(user=create_user_and_posts['user'])

    response = client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 1
    assert Like.objects.get().author.username == 'poster'
    assert Like.objects.get().post.title == 'publicpost'

    response = client.post(reverse('likes', kwargs={'post_pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 2
    assert Like.objects.all()[1].author.username == 'poster'
    assert Like.objects.all()[1].post.title == 'authenticatedpost'

    response = client.post(reverse('likes', kwargs={'post_pk': group_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 3
    assert Like.objects.all()[2].author.username == 'poster'
    assert Like.objects.all()[2].post.title == 'grouppost'

    response = client.post(reverse('likes', kwargs={'post_pk': private_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 4
    assert Like.objects.all()[3].author.username == 'poster'
    assert Like.objects.all()[3].post.title == 'privatepost'

    client.post(reverse('logout'))

def test_like_public_authenticated_and_group_posts(db, create_user_and_posts):
    client = APIClient()
    user = User.objects.create_user(username='reader', password='testpassword', team='testgroup1')
    client.force_authenticate(user=user)
    
    public_post = create_user_and_posts['public_post']
    authenticated_post = create_user_and_posts['authenticated_post']
    group_post = create_user_and_posts['group_post']
    private_post = create_user_and_posts['private_post']

    response = client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 1
    assert Like.objects.get().author.username == 'reader'
    assert Like.objects.get().post.title == 'publicpost'

    response = client.post(reverse('likes', kwargs={'post_pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 2
    assert Like.objects.all()[1].author.username == 'reader'
    assert Like.objects.all()[1].post.title == 'authenticatedpost'

    response = client.post(reverse('likes', kwargs={'post_pk': group_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 3
    assert Like.objects.all()[2].author.username == 'reader'
    assert Like.objects.all()[2].post.title == 'grouppost'

    response = client.post(reverse('likes', kwargs={'post_pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 3

    client.post(reverse('logout'))

def test_like_public_and_authenticated_posts(db, create_user_and_posts):
    client = APIClient()
    user = User.objects.create_user(username='reader', password='testpassword', team='testgroup2')
    client.force_authenticate(user=user)
    
    public_post = create_user_and_posts['public_post']
    authenticated_post = create_user_and_posts['authenticated_post']
    group_post = create_user_and_posts['group_post']
    private_post = create_user_and_posts['private_post']

    response = client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 1
    assert Like.objects.get().author.username == 'reader'
    assert Like.objects.get().post.title == 'publicpost'

    response = client.post(reverse('likes', kwargs={'post_pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert Like.objects.count() == 2
    assert Like.objects.all()[1].author.username == 'reader'
    assert Like.objects.all()[1].post.title == 'authenticatedpost'

    response = client.post(reverse('likes', kwargs={'post_pk': group_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 2

    response = client.post(reverse('likes', kwargs={'post_pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 2

    client.post(reverse('logout'))

def test_like_public_posts(client, db, create_user_and_posts):
    public_post = create_user_and_posts['public_post']
    authenticated_post = create_user_and_posts['authenticated_post']
    group_post = create_user_and_posts['group_post']
    private_post = create_user_and_posts['private_post']

    response = client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 0

    response = client.post(reverse('likes', kwargs={'post_pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 0

    response = client.post(reverse('likes', kwargs={'post_pk': group_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 0

    response = client.post(reverse('likes', kwargs={'post_pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 0
