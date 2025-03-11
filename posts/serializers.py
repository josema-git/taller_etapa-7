from rest_framework import serializers
from .models import Post, Comment, Like
from users.models import Blogger
from django.contrib.auth.models import User

class PostListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='blogger.user.username', read_only=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    team = serializers.CharField(source='blogger.team', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'likes', 'comments', 'team', 'created_at', 'updated_at'
                  'is_public', 'authenticated_permission', 'group_permission']
        
        def get_likes(self, obj):
            return Like.objects.filter(post=obj).count()

        def get_comments(self, obj):
            return Comment.objects.filter(post=obj).count()
        

class LikeSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='blogger.user.username', read_only=True)
    class Meta:
        model = Like
        fields = ['post', 'author', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='blogger.user.username', read_only=True)
    class Meta:
        model = Comment
        fields = ['post', 'author', 'content', 'created_at']