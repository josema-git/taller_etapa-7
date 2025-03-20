import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post, Comment

@pytest.fixture
def create_user_and_posts():
    user = User.objects.create_user(username='poster', password='testpassword', group_name='testgroup1')
    public_post = Post.objects.create(
        title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=user
    )
    authenticated_post = Post.objects.create(
        title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
        authenticated_permission=2, group_permission=2, author_permission=2, author=user
    )
    group_post = Post.objects.create(
        title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
        authenticated_permission=0, group_permission=2, author_permission=2, author=user
    )
    private_post = Post.objects.create(
        title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
        authenticated_permission=0, group_permission=0, author_permission=2, author=user
    )
    
    public_comment = Comment.objects.create(content='publiccomment', author=user, post=public_post)
    authenticated_comment = Comment.objects.create(content='authenticatedcomment', author=user, post=authenticated_post)
    group_comment = Comment.objects.create(content='groupcomment', author=user, post=group_post)
    private_comment = Comment.objects.create(content='privatecomment', author=user, post=private_post)

    return {
        "user": user,
        "public_post": public_post,
        "authenticated_post": authenticated_post,
        "group_post": group_post,
        "private_post": private_post,
        "public_comment": public_comment,
        "authenticated_comment": authenticated_comment,
        "group_comment": group_comment,
        "private_comment": private_comment,
    }


def test_update_and_delete_everything_as_author_or_superuser(client, db, create_user_and_posts):
    public_comment = create_user_and_posts['public_comment']
    authenticated_comment = create_user_and_posts['authenticated_comment']
    group_comment = create_user_and_posts['group_comment']
    private_comment = create_user_and_posts['private_comment']

    client.post(reverse('register'), {'username': 'poster', 'password': 'testpassword', 'group_name': 'testgroup1'})
    client.post(reverse('login'), {'username': 'poster', 'password': 'testpassword'})

    response = client.put(reverse('comment', kwargs={'pk': public_comment.id}), {'content': 'newcontent'}, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert Comment.objects.get(id=public_comment.id).content == 'newcontent'

    response = client.delete(reverse('comment', kwargs={'pk': public_comment.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Comment.objects.count() == 3

    response = client.put(reverse('comment', kwargs={'pk': authenticated_comment.id}), {'content': 'newcontent'}, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert Comment.objects.get(id=authenticated_comment.id).content == 'newcontent'

    response = client.delete(reverse('comment', kwargs={'pk': authenticated_comment.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Comment.objects.count() == 2

    response = client.put(reverse('comment', kwargs={'pk': group_comment.id}), {'content': 'newcontent'}, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert Comment.objects.get(id=group_comment.id).content == 'newcontent'

    response = client.delete(reverse('comment', kwargs={'pk': group_comment.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Comment.objects.count() == 1

    response = client.put(reverse('comment', kwargs={'pk': private_comment.id}), {'content': 'newcontent'}, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert Comment.objects.get(id=private_comment.id).content == 'newcontent'

    response = client.delete(reverse('comment', kwargs={'pk': private_comment.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Comment.objects.count() == 0

def test_update_and_delete_authenticated_or_group_comments(client, db, create_user_and_posts):
    user = User.objects.create_user(username='reader', password='testpassword', group_name='testgroup1')
    client.post(reverse('login'), {'username': 'reader', 'password': 'testpassword'})
    
    public_comment = create_user_and_posts['public_comment']

    response = client.put(reverse('comment', kwargs={'pk': public_comment.id}), {'content': 'newcontent'}, content_type='application/json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.get(id=public_comment.id).content == 'publiccomment'

    response = client.delete(reverse('comment', kwargs={'pk': public_comment.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.count() == 4

def test_update_and_delete_public_user_comments(client, db, create_user_and_posts):
    public_comment = create_user_and_posts['public_comment']

    response = client.put(reverse('comment', kwargs={'pk': public_comment.id}), {'content': 'newcontent'}, content_type='application/json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.get(id=public_comment.id).content == 'publiccomment'

    response = client.delete(reverse('comment', kwargs={'pk': public_comment.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.count() == 4
