import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post  
from rest_framework.test import APIClient

@pytest.fixture
def authenticated_client():
    client = APIClient()
    user = User.objects.create_user(username='testuser', password='testpassword', team='testgroup1')
    client.force_authenticate(user=user)
    return client

def test_success_create_post(db, authenticated_client):
    response = authenticated_client.post(reverse('posts'), {
        'title': 'testtitle',
        'content': 'testcontent',
        'is_public': '1',
        'authenticated_permission': 1,
        'group_permission': 1,
        'author_permission': 2
    })
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Post.objects.count() == 1
    
    post = Post.objects.get()
    assert post.title == 'testtitle'
    assert post.content == 'testcontent'
    assert post.is_public == 1
    assert post.authenticated_permission == 1
    assert post.group_permission == 1
    assert post.team == 'testgroup1'
    assert post.author.username == 'testuser'

def test_failed_create_post_unauthenticated(client, db):
    response = client.post(reverse('posts'), {
        'title': 'testtitle',
        'content': 'testcontent',
        'is_public': 1,
        'authenticated_permission': 1,
        'group_permission': 1,
        'author_permission': 2
    })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 0