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

def test_unlike_as_author_or_superuser(db, create_user_and_like):
    client = APIClient()
    like = create_user_and_like['like']

    client.force_authenticate(user=create_user_and_like['user'])
    response = client.delete(reverse('unlike', kwargs={'post_pk': create_user_and_like['public_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Like.objects.count() == 0

def test_unlike_as_anonymous(client, db, create_user_and_like):
    like = create_user_and_like['like']

    response = client.delete(reverse('unlike', kwargs={'post_pk': create_user_and_like['public_post'].id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 1
