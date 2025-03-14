from rest_framework import serializers
from .models import Post, Comment, Like

class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='User.username', read_only=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    group_name = serializers.CharField(source='User.group_name', read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'excerpt' , 'content', 'likes', 'comments', 'group_name', 'created_at', 'updated_at',
                  'is_public', 'authenticated_permission', 'group_permission', 'author_permission']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'likes', 'comments', 'group_name', 'excerpt']
        write_only_fields = ['is_public', 'authenticated_permission', 'group_permission', 'author_permission']
        
    def get_likes(self, obj):
        return Like.objects.filter(post=obj).count()

    def get_comments(self, obj):
        return Comment.objects.filter(post=obj).count()
    
    def get_excerpt(self, obj):
        return obj.content if len(obj.content) < 200 else obj.content[:200] + '...'
        
class PostDetailSerializer(PostListSerializer):

    def get_likes(self, obj):
        return LikeSerializer(Like.objects.filter(post=obj), many=True).data

    def get_comments(self, obj):
        return CommentSerializer(Comment.objects.filter(post=obj), many=True).data

class LikeSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Like
        fields = ['post', 'author_name' , 'created_at']
        read_only_fields = ['post', 'author_name', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Comment
        fields = ['post', 'author_name', 'content', 'created_at']
        read_only_fields = ['post', 'author_name', 'created_at']