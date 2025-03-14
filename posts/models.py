from django.db import models
from users.models import User

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    permission_options = (
        (0, 'none'),
        (1, 'read_only'),
        (2, 'read_and_write')
    )
    is_public = models.IntegerField(choices= ((0,'none'), (1,'read_only')), default='0')
    authenticated_permission = models.IntegerField(choices=permission_options, default='1')
    group_permission = models.IntegerField(choices=permission_options, default='1')
    author_permission = models.IntegerField(choices=((2, 'read_and_write'),), default=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)