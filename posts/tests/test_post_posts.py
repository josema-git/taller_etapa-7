import pytest
from django.urls import reverse
from rest_framework import status
from posts.models import Post  

@pytest.fixture
def authenticated_client(client):
    client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'testpassword',
        'group_name': 'testgroup1'
    })
    
    client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'testpassword'
    })
    
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
    assert post.group_name == 'testgroup1'
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