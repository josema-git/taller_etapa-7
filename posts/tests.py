from django.test import TestCase
from users.models import User
from .models import Post, Comment, Like
from django.urls import reverse
from rest_framework import status

# Create your tests here.


class ReadingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        self.client.post(reverse('posts'), {
            'title': 'publicpost',
            'content': 'publiccontent',
            'is_public': 1,
            'authenticated_permission': 1,
            'group_permission': 1,
            'author_permission': 2
        })
        self.client.post(reverse('posts'), {
            'title': 'authenticatedpost',
            'content': 'authenticatedcontent',
            'is_public': 0,
            'authenticated_permission': 1,
            'group_permission': 1,
            'author_permission': 2

        })
        self.client.post(reverse('posts'), {
            'title': 'grouppost',
            'content': 'groupcontent',
            'is_public': 0,
            'authenticated_permission': 0,
            'group_permission': 1,
            'author_permission': 2
        })
        self.client.post(reverse('posts'), {
            'title': 'privatepost',
            'content': 'privatecontent',
            'is_public': 0,
            'authenticated_permission': 0,
            'group_permission': 0,
            'author_permission': 2
        })
        self.client.post(reverse('logout'))

    def test_read_everything_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        self.assertEqual(response.data['results'][0]['title'], 'privatepost')
        self.assertEqual(response.data['results'][1]['title'], 'grouppost')
        self.assertEqual(response.data['results'][2]['title'], 'authenticatedpost')
        self.assertEqual(response.data['results'][3]['title'], 'publicpost')
        self.client.post(reverse('logout'))

    def test_read_public_authenticated_and_group_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['results'][0]['title'], 'grouppost')
        self.assertEqual(response.data['results'][1]['title'], 'authenticatedpost')
        self.assertEqual(response.data['results'][2]['title'], 'publicpost')
        self.client.post(reverse('logout'))

    def test_read_public_and_authenticated_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], 'authenticatedpost')
        self.assertEqual(response.data['results'][1]['title'], 'publicpost')
        self.client.post(reverse('logout'))

    def test_read_public_posts(self):
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'publicpost')

class IndividualReadingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=1, group_permission=1, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=1, group_permission=1, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=1, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )

    def test_read_everything_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'publicpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'authenticatedpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'grouppost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'privatepost')
        self.client.post(reverse('logout'))

    def test_read_public_authenticated_and_group_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'publicpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'authenticatedpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'grouppost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.post(reverse('logout'))

    def test_read_public_and_authenticated_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'publicpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'authenticatedpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.post(reverse('logout'))

    def test_read_public_posts(self):
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'publicpost')
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
class UpdatingOrDeletingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )

    def test_update_and_delete_everything_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.public_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.public_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 3)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.authenticated_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 2)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.group_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.group_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.private_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.private_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
        self.client.post(reverse('logout'))
    
    def test_update_and_delete_public_authenticated_and_group_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.public_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.public_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 3)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.authenticated_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 2)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.group_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.group_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.private_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.private_post.id).title, 'privatepost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)
        self.client.post(reverse('logout'))
    
    def test_update_and_delete_public_and_authenticated_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.public_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.public_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 3)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get(id=self.authenticated_post.id).title, 'newtitle')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 2)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.group_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.group_post.id).title, 'grouppost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 2)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.private_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.private_post.id).title, 'privatepost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 2)
        self.client.post(reverse('logout')) 
    
    def test_update_and_delete_public_posts(self):
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.public_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.public_post.id).title, 'publicpost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 4)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.authenticated_post.id).title, 'authenticatedpost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 4)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.group_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.group_post.id).title, 'grouppost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 4)
        response = self.client.put(reverse('detailed_post', kwargs={'pk': self.private_post.id}), {
            'title': 'newtitle',
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.get(id=self.private_post.id).title, 'privatepost')
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 4)

class CommentingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )
    
    def test_comment_everything_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.public_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, 'testcontent')
        self.assertEqual(Comment.objects.get().author.username, 'poster')
        self.assertEqual(Comment.objects.get().post.title, 'publicpost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.all()[1].content, 'testcontent')
        self.assertEqual(Comment.objects.all()[1].author.username, 'poster')
        self.assertEqual(Comment.objects.all()[1].post.title, 'authenticatedpost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.group_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Comment.objects.all()[2].content, 'testcontent')
        self.assertEqual(Comment.objects.all()[2].author.username, 'poster')
        self.assertEqual(Comment.objects.all()[2].post.title, 'grouppost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.private_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 4)
        self.client.post(reverse('logout'))

    def test_comment_public_authenticated_and_group_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.public_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, 'testcontent')
        self.assertEqual(Comment.objects.get().author.username, 'reader')
        self.assertEqual(Comment.objects.get().post.title, 'publicpost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.all()[1].content, 'testcontent')
        self.assertEqual(Comment.objects.all()[1].author.username, 'reader')
        self.assertEqual(Comment.objects.all()[1].post.title, 'authenticatedpost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.group_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Comment.objects.all()[2].content, 'testcontent')
        self.assertEqual(Comment.objects.all()[2].author.username, 'reader')
        self.assertEqual(Comment.objects.all()[2].post.title, 'grouppost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.private_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 3)
        self.client.post(reverse('logout'))

    def test_comment_public_and_authenticated_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.public_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, 'testcontent')
        self.assertEqual(Comment.objects.get().author.username, 'reader')
        self.assertEqual(Comment.objects.get().post.title, 'publicpost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.all()[1].content, 'testcontent')
        self.assertEqual(Comment.objects.all()[1].author.username, 'reader')
        self.assertEqual(Comment.objects.all()[1].post.title, 'authenticatedpost')
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.group_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 2)
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.private_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 2)
        self.client.post(reverse('logout'))

    def test_comment_public_posts(self):
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.public_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.group_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)
        response = self.client.post(reverse('comments', kwargs={'post_pk': self.private_post.id}), {
            'content': 'testcontent'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)

class UpdatingOrDeletingCommentsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )
        self.public_comment = Comment.objects.create(
            content='publiccomment', author=self.user, post=self.public_post
        )
        self.authenticated_comment = Comment.objects.create(
            content='authenticatedcomment', author=self.user, post=self.authenticated_post
        )
        self.group_comment = Comment.objects.create(
            content='groupcomment', author=self.user, post=self.group_post
        )
        self.private_comment = Comment.objects.create(
            content='privatecomment', author=self.user, post=self.private_post
        )
    
    def test_update_and_delete_everything_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.put(reverse('comment', kwargs={'pk': self.public_comment.id}), {
            'content': 'newcontent'
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.get(id=self.public_comment.id).content, 'newcontent')
        response = self.client.delete(reverse('comment', kwargs={'pk': self.public_comment.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 3)
        response = self.client.put(reverse('comment', kwargs={'pk': self.authenticated_comment.id}), {
            'content': 'newcontent'
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.get(id=self.authenticated_comment.id).content, 'newcontent')
        response = self.client.delete(reverse('comment', kwargs={'pk': self.authenticated_comment.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 2)
        response = self.client.put(reverse('comment', kwargs={'pk': self.group_comment.id}), {
            'content': 'newcontent'
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.get(id=self.group_comment.id).content, 'newcontent')
        response = self.client.delete(reverse('comment', kwargs={'pk': self.group_comment.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 1)
        response = self.client.put(reverse('comment', kwargs={'pk': self.private_comment.id}), {
            'content': 'newcontent'
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.get(id=self.private_comment.id).content, 'newcontent')
        response = self.client.delete(reverse('comment', kwargs={'pk': self.private_comment.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
        self.client.post(reverse('logout'))

    def test_update_and_delete_authenticated_or_group_comments(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.put(reverse('comment', kwargs={'pk': self.public_comment.id}), {
            'content': 'newcontent'
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.get(id=self.public_comment.id).content, 'publiccomment')
        response = self.client.delete(reverse('comment', kwargs={'pk': self.public_comment.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 4)

    def test_update_and_delete_public_user_comments(self):
        response = self.client.put(reverse('comment', kwargs={'pk': self.public_comment.id}), {
            'content': 'newcontent'
        },content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.get(id=self.public_comment.id).content, 'publiccomment')
        response = self.client.delete(reverse('comment', kwargs={'pk': self.public_comment.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 4)

class LikingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )

    def test_like_everything_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.get().author.username, 'poster')
        self.assertEqual(Like.objects.get().post.title, 'publicpost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 2)
        self.assertEqual(Like.objects.all()[1].author.username, 'poster')
        self.assertEqual(Like.objects.all()[1].post.title, 'authenticatedpost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 3)
        self.assertEqual(Like.objects.all()[2].author.username, 'poster')
        self.assertEqual(Like.objects.all()[2].post.title, 'grouppost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 4)
        self.assertEqual(Like.objects.all()[3].author.username, 'poster')
        self.assertEqual(Like.objects.all()[3].post.title, 'privatepost')
        self.client.post(reverse('logout'))
    
    def test_like_public_authenticated_and_group_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.get().author.username, 'reader')
        self.assertEqual(Like.objects.get().post.title, 'publicpost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 2)
        self.assertEqual(Like.objects.all()[1].author.username, 'reader')
        self.assertEqual(Like.objects.all()[1].post.title, 'authenticatedpost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 3)
        self.assertEqual(Like.objects.all()[2].author.username, 'reader')
        self.assertEqual(Like.objects.all()[2].post.title, 'grouppost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 3)
        self.client.post(reverse('logout'))

    def test_like_public_and_authenticated_posts(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.get().author.username, 'reader')
        self.assertEqual(Like.objects.get().post.title, 'publicpost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 2)
        self.assertEqual(Like.objects.all()[1].author.username, 'reader')
        self.assertEqual(Like.objects.all()[1].post.title, 'authenticatedpost')
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 2)
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 2)
        self.client.post(reverse('logout'))
    
    def test_like_public_posts(self):
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 0)
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 0)
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 0)
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 0)

class UnlikingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.like = Like.objects.create(author=self.user, post=self.public_post)
    
    def test_unlike_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.delete(reverse('unlike', kwargs={'pk': self.like.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)
        self.client.post(reverse('logout'))
    
    def test_unlike_as_user(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        response = self.client.delete(reverse('unlike', kwargs={'pk': self.like.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 1)
        self.client.post(reverse('logout'))
    
    def test_unlike_as_anonymous(self):
        response = self.client.delete(reverse('unlike', kwargs={'pk': self.like.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 1)

class DoubleLikingPostsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.like = Like.objects.create(author=self.user, post=self.public_post)

    def test_double_like_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 1)
        self.client.post(reverse('logout'))
    
    def test_double_like_as_user(self):
        self.client.post(reverse('register'),{
            'username': 'reader',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('login'), {
            'username': 'reader',
            'password': 'testpassword'
        })
        self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(Like.objects.count(), 2)
        response = self.client.post(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 2)
        self.client.post(reverse('logout'))

class LikesListsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.like = Like.objects.create(author=self.user, post=self.public_post)
        self.client.post(reverse('register'),{
            'username': 'liker1',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.liker1 = User.objects.get(username='liker1')
        self.client.post(reverse('register'),{
            'username': 'liker2',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.liker2 = User.objects.get(username='liker2')
        self.like1 = Like.objects.create(author=self.liker1, post=self.public_post)
        self.like2 = Like.objects.create(author=self.liker2, post=self.public_post)

    def test_get_likes_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.client.post(reverse('logout'))
    
    def test_get_likes_as_user(self):
        self.client.post(reverse('login'), {
            'username': 'liker1',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.client.post(reverse('logout'))
    
    def test_get_likes_as_anonymous(self):
        response = self.client.get(reverse('likes', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class LikesAllOrFilteredByAuthorTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )
        self.public_like = Like.objects.create(author=self.user, post=self.public_post)
        self.authenticated_like = Like.objects.create(author=self.user, post=self.authenticated_post)
        self.group_like = Like.objects.create(author=self.user, post=self.group_post)
        self.private_like = Like.objects.create(author=self.user, post=self.private_post)
        self.client.post(reverse('register'),{
            'username': 'liker1',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.liker1 = User.objects.get(username='liker1')
        self.public_like1 = Like.objects.create(author=self.liker1, post=self.public_post)
        self.authenticated_like1 = Like.objects.create(author=self.liker1, post=self.authenticated_post)
        self.group_like1 = Like.objects.create(author=self.liker1, post=self.group_post)

    def test_get_all_likes_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('all_likes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)
        self.client.post(reverse('logout'))
    
    def test_get_all_likes_as_user(self):
        self.client.post(reverse('login'), {
            'username': 'liker1',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('all_likes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)
        self.client.post(reverse('logout'))

    def test_get_all_likes_as_diff_group_user(self):
        self.client.post(reverse('register'),{
            'username': 'liker2',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'liker2',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('all_likes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        self.client.post(reverse('logout'))
    
    def test_get_all_likes_as_anonymous(self):
        response = self.client.get(reverse('all_likes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_likes_filtered_by_author_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('specific_user_likes', kwargs={'user_pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        response = self.client.get(reverse('specific_user_likes', kwargs={'user_pk': self.liker1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.client.post(reverse('logout'))
    
    def test_get_likes_filtered_by_author_as_user(self):
        self.client.post(reverse('login'), {
            'username': 'liker1',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('specific_user_likes', kwargs={'user_pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        response = self.client.get(reverse('specific_user_likes', kwargs={'user_pk': self.liker1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.client.post(reverse('logout'))
    
    def test_get_likes_filtered_by_author_as_anonymous(self):
        response = self.client.get(reverse('specific_user_likes', kwargs={'user_pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        response = self.client.get(reverse('specific_user_likes', kwargs={'user_pk': self.liker1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class CommentsListsTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )
        self.public_comment = Comment.objects.create(
            content='publiccomment', author=self.user, post=self.public_post
        )
        self.authenticated_comment = Comment.objects.create(
            content='authenticatedcomment', author=self.user, post=self.authenticated_post
        )
        self.group_comment = Comment.objects.create(
            content='groupcomment', author=self.user, post=self.group_post
        )
        self.private_comment = Comment.objects.create(
            content='privatecomment', author=self.user, post=self.private_post
        )
        self.client.post(reverse('register'),{
            'username': 'commenter1',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.commenter1 = User.objects.get(username='commenter1')
        self.public_comment1 = Comment.objects.create(
            content='publiccomment1', author=self.commenter1, post=self.public_post
        )
        self.authenticated_comment1 = Comment.objects.create(
            content='authenticatedcomment1', author=self.commenter1, post=self.authenticated_post
        )
        self.group_comment1 = Comment.objects.create(
            content='groupcomment1', author=self.commenter1, post=self.group_post
        )

    def test_get_comments_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.client.post(reverse('logout'))

    def test_get_comments_as_user(self):
        self.client.post(reverse('login'), {
            'username': 'commenter1',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.post(reverse('logout'))
    
    def test_get_comments_as_anonymous(self):
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.authenticated_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.group_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(reverse('comments', kwargs={'post_pk': self.private_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
class CommentsAllOrFilteredByAuthorTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.authenticated_post = Post.objects.create(
            title='authenticatedpost', content='authenticatedcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.group_post = Post.objects.create(
            title='grouppost', content='groupcontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=2, author_permission=2, author=self.user
        )
        self.private_post = Post.objects.create(
            title='privatepost', content='privatecontent', is_public=0, group_name='testgroup1',
            authenticated_permission=0, group_permission=0, author_permission=2, author=self.user
        )
        self.public_comment = Comment.objects.create(
            content='publiccomment', author=self.user, post=self.public_post
        )
        self.authenticated_comment = Comment.objects.create(
            content='authenticatedcomment', author=self.user, post=self.authenticated_post
        )
        self.group_comment = Comment.objects.create(
            content='groupcomment', author=self.user, post=self.group_post
        )
        self.private_comment = Comment.objects.create(
            content='privatecomment', author=self.user, post=self.private_post
        )
        self.client.post(reverse('register'),{
            'username': 'commenter1',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.commenter1 = User.objects.get(username='commenter1')
        self.public_comment1 = Comment.objects.create(
            content='publiccomment1', author=self.commenter1, post=self.public_post
        )
        self.authenticated_comment1 = Comment.objects.create(
            content='authenticatedcomment1', author=self.commenter1, post=self.authenticated_post
        )
        self.group_comment1 = Comment.objects.create(
            content='groupcomment1', author=self.commenter1, post=self.group_post
        )

    def test_get_all_comments_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('all_comments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)
        self.client.post(reverse('logout'))
    
    def test_get_all_comments_as_user(self):
        self.client.post(reverse('login'), {
            'username': 'commenter1',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('all_comments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)
        self.client.post(reverse('logout'))
    
    def test_get_all_comments_as_diff_group_user(self):
        self.client.post(reverse('register'),{
            'username': 'commenter2',
            'password': 'testpassword',
            'group_name': 'testgroup2'
        })
        self.client.post(reverse('login'), {
            'username': 'commenter2',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('all_comments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        self.client.post(reverse('logout'))

    def test_get_all_comments_as_anonymous(self):
        response = self.client.get(reverse('all_comments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_comments_filtered_by_author_as_author_or_superuser(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('specific_user_comments', kwargs={'user_pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        response = self.client.get(reverse('specific_user_comments', kwargs={'user_pk': self.commenter1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.client.post(reverse('logout'))
    
    def test_get_comments_filtered_by_author_as_user(self):
        self.client.post(reverse('login'), {
            'username': 'commenter1',
            'password': 'testpassword'
        })
        response = self.client.get(reverse('specific_user_comments', kwargs={'user_pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        response = self.client.get(reverse('specific_user_comments', kwargs={'user_pk': self.commenter1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.client.post(reverse('logout'))
    
    def test_get_comments_filtered_by_author_as_anonymous(self):
        response = self.client.get(reverse('specific_user_comments', kwargs={'user_pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        response = self.client.get(reverse('specific_user_comments', kwargs={'user_pk': self.commenter1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class CascadeRemovingCommentsAndLikesTestCase(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), {
            'username': 'poster',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.client.post(reverse('register'), {
            'username': 'commenter',
            'password': 'testpassword',
            'group_name': 'testgroup1'
        })
        self.user = User.objects.get(username='poster')
        self.commenter = User.objects.get(username='commenter')
        self.public_post = Post.objects.create(
            title='publicpost', content='publiccontent', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.comment1 = Comment.objects.create(
            content='comment1', author=self.user, post=self.public_post
        )
        self.comment2 = Comment.objects.create(
            content='comment2', author=self.commenter, post=self.public_post
        )
        self.like1 = Like.objects.create(author=self.user, post=self.public_post)
        self.like2 = Like.objects.create(author=self.commenter, post=self.public_post)

        self.public_post2 = Post.objects.create(
            title='publicpost2', content='publiccontent2', is_public=1, group_name='testgroup1',
            authenticated_permission=2, group_permission=2, author_permission=2, author=self.user
        )
        self.comment3 = Comment.objects.create(
            content='comment3', author=self.user, post=self.public_post2
        )
        self.comment4 = Comment.objects.create(
            content='comment4', author=self.commenter, post=self.public_post2
        )
        self.like3 = Like.objects.create(author=self.user, post=self.public_post2)
        self.like4 = Like.objects.create(author=self.commenter, post=self.public_post2)

    def test_cascade_remove_comments_and_likes(self):
        self.client.post(reverse('login'), {
            'username': 'poster',
            'password': 'testpassword'
        })
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Like.objects.count(), 2)
        self.client.post(reverse('logout'))
    
    def test_cascade_remove_comments_and_likes_as_commenter(self):
        self.client.post(reverse('login'), {
            'username': 'commenter',
            'password': 'testpassword'
        })
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Like.objects.count(), 2)
        self.client.post(reverse('logout'))

    def test_cascade_remove_comments_and_likes_as_anonymous(self):
        response = self.client.delete(reverse('detailed_post', kwargs={'pk': self.public_post.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Comment.objects.count(), 4)
        self.assertEqual(Like.objects.count(), 4)
