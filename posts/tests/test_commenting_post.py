import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from posts.models import Post 

@pytest.fixture
def setup_posts(client):
    # Registrar un usuario
    client.post(reverse('register'), {
        'username': 'poster',
        'password': 'testpassword',
        'group_name': 'testgroup1'
    })
    
    # Obtener el usuario registrado
    user = User.objects.get(username='poster')
    
    # Crear posts
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
    
    return {
        'user': user,
        'public_post': public_post,
        'authenticated_post': authenticated_post,
        'group_post': group_post,
        'private_post': private_post
    }

def test_update_and_delete_everything_as_author_or_superuser(client, db, setup_posts):
    client.post(reverse('login'), {
        'username': 'poster',
        'password': 'testpassword'
    })
    
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': public_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=public_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 3
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': authenticated_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=authenticated_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 2
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': group_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=group_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 1
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': private_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=private_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 0
    
    # Cerrar sesión
    client.post(reverse('logout'))

def test_update_and_delete_public_authenticated_and_group_posts(client, db, setup_posts):
    client.post(reverse('register'), {
        'username': 'reader',
        'password': 'testpassword',
        'group_name': 'testgroup1'
    })
    client.post(reverse('login'), {
        'username': 'reader',
        'password': 'testpassword'
    })
    
    # Obtener los posts creados en la fixture
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': public_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=public_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 3
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': authenticated_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=authenticated_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 2
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': group_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=group_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 1
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': private_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=private_post.id).title == 'privatepost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 1
    
    client.post(reverse('logout'))

def test_update_and_delete_public_and_authenticated_posts(client, db, setup_posts):
    client.post(reverse('register'), {
        'username': 'reader',
        'password': 'testpassword',
        'group_name': 'testgroup2'
    })
    client.post(reverse('login'), {
        'username': 'reader',
        'password': 'testpassword'
    })
    
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': public_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=public_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 3
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': authenticated_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert Post.objects.get(id=authenticated_post.id).title == 'newtitle'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Post.objects.count() == 2
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': group_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=group_post.id).title == 'grouppost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 2
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': private_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=private_post.id).title == 'privatepost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 2
    
    # Cerrar sesión
    client.post(reverse('logout'))

def test_update_and_delete_public_posts(client, db, setup_posts):
    public_post = setup_posts['public_post']
    authenticated_post = setup_posts['authenticated_post']
    group_post = setup_posts['group_post']
    private_post = setup_posts['private_post']
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': public_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=public_post.id).title == 'publicpost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': public_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 4
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': authenticated_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=authenticated_post.id).title == 'authenticatedpost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': authenticated_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 4
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': group_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=group_post.id).title == 'grouppost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': group_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 4
    
    response = client.put(
        reverse('detailed_post', kwargs={'pk': private_post.id}),
        {'title': 'newtitle'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.get(id=private_post.id).title == 'privatepost'
    
    response = client.delete(reverse('detailed_post', kwargs={'pk': private_post.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.count() == 4