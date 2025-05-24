import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Comment, Like

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

    Like.objects.create(author=poster, post=public_post)
    Like.objects.create(author=poster, post=authenticated_post)
    Like.objects.create(author=poster, post=group_post)
    Like.objects.create(author=poster, post=private_post)
    Like.objects.create(author=commenter1, post=public_post)
    Like.objects.create(author=commenter1, post=authenticated_post)
    Like.objects.create(author=commenter1, post=group_post)
    
    return {
        'poster': poster,
        'commenter1': commenter1,
        'commenter2': commenter2,
        'public_post': public_post,
        'authenticated_post': authenticated_post,
        'group_post': group_post,
        'private_post': private_post,
    }


def test_cascade_remove_comments_and_likes(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})
    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['public_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 3 
    assert Comment.objects.count() == 5
    assert Like.objects.count() == 5

    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['authenticated_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 2
    assert Comment.objects.count() == 3
    assert Like.objects.count() == 3

    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['group_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 1
    assert Comment.objects.count() == 1
    assert Like.objects.count() == 1

    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['private_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 0
    assert Comment.objects.count() == 0
    assert Like.objects.count() == 0

    client.post(reverse('logout'))


def test_cascade_remove_comments_and_likes_as_commenter(client, db, create_users_and_comments):
    client.post(reverse('login'), {'username': 'commenter1', 'password': 'testpassword'})
    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['public_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 3
    assert Comment.objects.count() == 5
    assert Like.objects.count() == 5

    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['authenticated_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 2
    assert Comment.objects.count() == 3
    assert Like.objects.count() == 3

    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['group_post'].id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 1
    assert Comment.objects.count() == 1
    assert Like.objects.count() == 1

    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['private_post'].id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 1
    assert Comment.objects.count() == 1
    assert Like.objects.count() == 1

    client.post(reverse('logout'))


def test_cascade_remove_comments_and_likes_as_anonymous(client, db, create_users_and_comments):
    response = client.delete(reverse('detailed_post', kwargs={'pk': create_users_and_comments['public_post'].id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 4
    assert Comment.objects.count() == 7 
    assert Like.objects.count() == 7