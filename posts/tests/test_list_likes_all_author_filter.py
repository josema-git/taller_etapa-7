import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Comment

@pytest.fixture
def create_users_and_comments():
    poster = User.objects.create_user(username='poster', password='testpassword', group_name='testgroup1')
    commenter1 = User.objects.create_user(username='commenter1', password='testpassword', group_name='testgroup1')
    
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=poster
    )
    authenticated_post = Post.objects.create(
        title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=poster
    )
    group_post = Post.objects.create(
        title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
        authenticated_permission=0, group_permission=2, author_permission=2, author=poster
    )
    private_post = Post.objects.create(
        title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
        authenticated_permission=0, group_permission=0, author_permission=2, author=poster
    )
    
    Comment.objects.create(content='publiccomment', author=poster, post=public_post)
    Comment.objects.create(content='authenticatedcomment', author=poster, post=authenticated_post)
    Comment.objects.create(content='groupcomment', author=poster, post=group_post)
    Comment.objects.create(content='privatecomment', author=poster, post=private_post)
    Comment.objects.create(content='publiccomment1', author=commenter1, post=public_post)
    Comment.objects.create(content='authenticatedcomment1', author=commenter1, post=authenticated_post)
    Comment.objects.create(content='groupcomment1', author=commenter1, post=group_post)
    
    return {
        'poster': poster,
        'commenter1': commenter1,
        'public_post': public_post,
        'authenticated_post': authenticated_post,
        'group_post': group_post,
        'private_post': private_post,
    }


def test_get_comments_as_author_or_superuser(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})
    
    for post_key in ['public_post', 'authenticated_post', 'group_post', 'private_post']:
        post = create_users_and_comments[post_key]
        response = client.get(reverse('comments', kwargs={'post_pk': post.id}))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == (2 if post_key != 'private_post' else 1)
    
    client.post(reverse('logout'))


def test_get_comments_as_user(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'commenter1', 'password': 'testpassword'})
    
    for post_key in ['public_post', 'authenticated_post', 'group_post']:
        post = create_users_and_comments[post_key]
        response = client.get(reverse('comments', kwargs={'post_pk': post.id}))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    private_post = create_users_and_comments['private_post']
    response = client.get(reverse('comments', kwargs={'post_pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    client.post(reverse('logout'))


def test_get_comments_as_anonymous(client, db, create_users_and_comments):
    public_post = create_users_and_comments['public_post']
    response = client.get(reverse('comments', kwargs={'post_pk': public_post.id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
    
    for post_key in ['authenticated_post', 'group_post', 'private_post']:
        post = create_users_and_comments[post_key]
        response = client.get(reverse('comments', kwargs={'post_pk': post.id}))
        assert response.status_code == status.HTTP_403_FORBIDDEN
