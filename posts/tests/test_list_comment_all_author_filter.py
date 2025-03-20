import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Comment

@pytest.fixture
def create_users_and_comments():
    poster = User.objects.create_user(username='poster', password='testpassword', group_name='testgroup1')
    commenter1 = User.objects.create_user(username='commenter1', password='testpassword', group_name='testgroup1')
    commenter2 = User.objects.create_user(username='commenter2', password='testpassword', group_name='testgroup2')
    
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
        'commenter2': commenter2,
        'public_post': public_post,
        'authenticated_post': authenticated_post,
        'group_post': group_post,
        'private_post': private_post,
    }


def test_get_all_comments_as_author_or_superuser(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})
    response = client.get(reverse('all_comments'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 7
    client.post(reverse('logout'))


def test_get_all_comments_as_user(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'commenter1', 'password': 'testpassword'})
    response = client.get(reverse('all_comments'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 6
    client.post(reverse('logout'))


def test_get_all_comments_as_diff_group_user(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'commenter2', 'password': 'testpassword'})
    response = client.get(reverse('all_comments'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 4
    client.post(reverse('logout'))


def test_get_all_comments_as_anonymous(client, db, create_users_and_comments):
    response = client.get(reverse('all_comments'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


def test_get_comments_filtered_by_author_as_author_or_superuser(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})
    response = client.get(reverse('specific_user_comments', kwargs={'user_pk': create_users_and_comments['poster'].id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 4
    response = client.get(reverse('specific_user_comments', kwargs={'user_pk': create_users_and_comments['commenter1'].id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    client.post(reverse('logout'))


def test_get_comments_filtered_by_author_as_user(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'commenter1', 'password': 'testpassword'})
    response = client.get(reverse('specific_user_comments', kwargs={'user_pk': create_users_and_comments['poster'].id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    response = client.get(reverse('specific_user_comments', kwargs={'user_pk': create_users_and_comments['commenter1'].id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    client.post(reverse('logout'))


def test_get_comments_filtered_by_author_as_anonymous(client, db, create_users_and_comments):
    response = client.get(reverse('specific_user_comments', kwargs={'user_pk': create_users_and_comments['poster'].id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    response = client.get(reverse('specific_user_comments', kwargs={'user_pk': create_users_and_comments['commenter1'].id}))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
