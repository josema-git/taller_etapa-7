import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Like

@pytest.fixture
def create_user_and_like():
    user = User.objects.create_user(username='poster', password='testpassword', group_name='testgroup1')
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=user
    )
    like = Like.objects.create(author=user, post=public_post)
    return {
        'user': user,
        'public_post': public_post,
        'like': like,
    }

def test_unlike_as_author_or_superuser(client, db, create_user_and_like):
    like = create_user_and_like['like']

    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})

    response = client.delete(reverse('unlike', kwargs={'pk': like.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Like.objects.count() == 0

    client.post(reverse('logout'))

def test_unlike_as_user(client, db, create_user_and_like):
    client.post(reverse('register'), {'username': 'reader', 'password': 'testpassword', 'group_name': 'testgroup1'})
    client.post(reverse('login'), {'username': 'reader', 'password': 'testpassword'})
    
    like = create_user_and_like['like']

    response = client.delete(reverse('unlike', kwargs={'pk': like.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 1

    client.post(reverse('logout'))

def test_unlike_as_anonymous(client, db, create_user_and_like):
    like = create_user_and_like['like']

    response = client.delete(reverse('unlike', kwargs={'pk': like.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Like.objects.count() == 1
