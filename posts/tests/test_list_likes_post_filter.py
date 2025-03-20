import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Like

@pytest.fixture
def create_users_and_likes():
    poster = User.objects.create_user(username='poster', password='testpassword', group_name='testgroup1')
    liker1 = User.objects.create_user(username='liker1', password='testpassword', group_name='testgroup1')
    liker2 = User.objects.create_user(username='liker2', password='testpassword', group_name='testgroup1')
    
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=poster
    )
    
    like_poster = Like.objects.create(author=poster, post=public_post)
    like1 = Like.objects.create(author=liker1, post=public_post)
    like2 = Like.objects.create(author=liker2, post=public_post)
    
    return {
        'poster': poster,
        'liker1': liker1,
        'liker2': liker2,
        'public_post': public_post,
        'like': like_poster,
    }


def test_get_likes_as_author_or_superuser(client, db, create_users_and_likes):
    public_post = create_users_and_likes['public_post']

    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})
    response = client.get(reverse('likes', kwargs={'post_pk': public_post.id}))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    
    client.post(reverse('logout'))


def test_get_likes_as_user(client, db, create_users_and_likes):
    client.post(reverse('register'), {'username': 'liker1', 'password': 'testpassword', 'group_name': 'testgroup1'})
    client.post(reverse('login'), {'username': 'liker1', 'password': 'testpassword'})
    
    public_post = create_users_and_likes['public_post']
    response = client.get(reverse('likes', kwargs={'post_pk': public_post.id}))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    
    client.post(reverse('logout'))


def test_get_likes_as_anonymous(client, db, create_users_and_likes):
    public_post = create_users_and_likes['public_post']
    response = client.get(reverse('likes', kwargs={'post_pk': public_post.id}))
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3