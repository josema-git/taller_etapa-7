import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Like
from rest_framework.test import APIClient

@pytest.fixture
def create_user_and_like():
    user = User.objects.create_user(username='poster', password='testpassword', team='testgroup1')
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, team='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=user
    )
    like = Like.objects.create(author=user, post=public_post)
    return {
        'user': user,
        'public_post': public_post,
        'like': like,
    }


def test_double_like_as_author_or_superuser(db, create_user_and_like):
    client = APIClient()
    create_user_and_like['like']
    public_post = create_user_and_like['public_post']

    client.force_authenticate(user=create_user_and_like['user'])

    response = client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 1

    client.post(reverse('logout'))

def test_double_like_as_user(db, create_user_and_like):
    client = APIClient()
    user = User.objects.create_user(username='reader', password='testpassword', team='testgroup1')
    client.force_authenticate(user=user)

    public_post = create_user_and_like['public_post']
    
    client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert Like.objects.count() == 2
    
    response = client.post(reverse('likes', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 2

    client.post(reverse('logout'))
