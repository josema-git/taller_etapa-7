from rest_framework import serializers
from .models import Post, Comment, Like
from users.models import User
from posts.permissions import VisibleAndEditableBlogs

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    permission_level = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'excerpt' , 'content', 'likes', 'comments', 'team', 'created_at', 'updated_at',
                  'is_public', 'authenticated_permission', 'group_permission', 'author_permission', 'permission_level', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'likes', 'comments', 'team', 'excerpt','is_liked' ,'permission_level']
        write_only_fields = ['is_public', 'authenticated_permission', 'group_permission', 'author_permission']

    def get_author(self, obj):
        return User.objects.get(id=obj.author.id).username
        
    def get_likes(self, obj):
        return Like.objects.filter(post=obj).count()

    def get_comments(self, obj):
        return Comment.objects.filter(post=obj).count()
    
    def get_excerpt(self, obj):
        return obj.content if len(obj.content) < 200 else obj.content[:200] + '...'

    def get_permission_level(self, obj):
        return VisibleAndEditableBlogs().permission_level(self.context['request'], obj)
    
    def get_is_liked(self, obj):
        if self.context['request'].user.is_authenticated:
            return Like.objects.filter(post=obj, author=self.context['request'].user).exists()
        return False

class LikeSerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Like
        fields = ['post', 'author' , 'created_at']
        read_only_fields = ['post', 'author', 'created_at']

    def get_author(self, obj):
        return User.objects.get(id=obj.author.id).username

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField()
    class Meta:
        model = Comment
        fields = ['post', 'author', 'content', 'created_at']
        read_only_fields = ['post', 'author', 'created_at']

    def get_author(self, obj):
        return User.objects.get(id=obj.author.id).username