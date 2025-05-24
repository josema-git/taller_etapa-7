from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .pagination import LikePagination, PostPagination, CommentPagination
from .models import Post, Comment, Like
from .serializers import PostSerializer , LikeSerializer, CommentSerializer
from .permissions import VisibleAndEditableBlogs

class PostViewset(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def create(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'You are not authenticated'}, status=status.HTTP_403_FORBIDDEN)
        try:
            author = request.user
            team = request.user.team
            title = request.data.get('title')
            content = request.data.get('content')
            is_public = request.data.get('is_public')
            authenticated_permission = request.data.get('authenticated_permission')
            group_permission = request.data.get('group_permission')
            author_permission = request.data.get('author_permission')
            Post.objects.create(author=author, team=team, title=title, content=content, is_public=is_public, authenticated_permission=authenticated_permission, group_permission=group_permission, author_permission=author_permission)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'Post created successfully', }, status=status.HTTP_201_CREATED)
    
    def list(self, request):
        posts = Post.objects.all()
        visible_posts = []
        for post in posts:
            if VisibleAndEditableBlogs().has_read_permission(request, post):
                visible_posts.append(post)
        visible_posts = sorted(visible_posts, key=lambda post: post.created_at, reverse=True)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_posts, request)
        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def update(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        if not VisibleAndEditableBlogs().has_edit_permission(request, post):
            return Response({'error': 'No tienes permiso para editar este post'}, status=status.HTTP_403_FORBIDDEN)
        
        permitted_data = {
            'user': request.user,
            'team': request.user.team,
            'title': request.data.get('title', post.title),
            'content': request.data.get('content', post.content),
            'is_public': request.data.get('is_public', post.is_public),
            'authenticated_permission': request.data.get('authenticated_permission', post.authenticated_permission),
            'group_permission': request.data.get('group_permission', post.group_permission),
            'author_permission': request.data.get('author_permission', post.author_permission),
        }
        serializer = self.get_serializer(post, data=permitted_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        if not VisibleAndEditableBlogs().has_edit_permission(request, post):
            return Response({'error': 'You do not have permission to delete this post'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({'success': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, pk): 
        try:
            post = Post.objects.get(pk=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        if not VisibleAndEditableBlogs().has_read_permission(request, post):
            return Response({'error': 'You do not have permission to view this post'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def create(self, request, post_pk):
        if not request.user.is_authenticated:
            return Response({'error': 'You are not authenticated'}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = Post.objects.get(pk=post_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if not VisibleAndEditableBlogs().has_read_permission(request, post):
            return Response({'error': 'You do not have permission to comment on this post'}, status=status.HTTP_403_FORBIDDEN)
        Comment.objects.create(author=request.user, post=post, content=request.data.get('content'))
        return Response({'success': 'Comment created successfully'}, status=status.HTTP_201_CREATED)
    
    def list_posts(self, request, post_pk):
        try:
            post = Post.objects.get(pk=post_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        if not VisibleAndEditableBlogs().has_read_permission(request, post):
            return Response({'error': 'You do not have permission to view comments on this post'}, status=status.HTTP_403_FORBIDDEN)

        comments = Comment.objects.filter(post=post)
        visible_comments = sorted(comments, key=lambda comment: comment.created_at, reverse=True)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve_users(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        comments = Comment.objects.filter(author=user)
        visible_comments = []

        for comment in comments:
            if VisibleAndEditableBlogs().has_read_permission(request, comment.post):
                visible_comments.append(comment)
        
        visible_comments = sorted(visible_comments, key=lambda comment: comment.created_at, reverse=True)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def list_all(self, request):
        comments = Comment.objects.all()
        visible_comments = []
        for comment in comments:
            if VisibleAndEditableBlogs().has_read_permission(request, comment.post):
                visible_comments.append(comment)
        
        visible_comments = sorted(visible_comments, key=lambda comment: comment.created_at, reverse=True)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def destroy(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user != comment.author:
            return Response({'error': 'You do not have permission to delete this comment'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({'success': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user != comment.author:
            return Response({'error': 'You do not have permission to edit this comment'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        if request.user != comment.author:
            return Response({'error': 'You do not have permission to view this comment'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LikeViewset(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    pagination_class = LikePagination

    def list_posts(self, request, post_pk):
        try:
            post = Post.objects.get(pk=post_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        if not VisibleAndEditableBlogs().has_read_permission(request, post):
            return Response({'error': 'You do not have permission to view likes on this post'}, status=status.HTTP_403_FORBIDDEN)
        
        likes = Like.objects.filter(post=post)
        visible_likes = sorted(likes, key=lambda like: like.created_at, reverse=True)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_likes, request)
        serializer = LikeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve_users(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        likes = Like.objects.filter(author=user)
        visible_likes = []

        for like in likes:
            if VisibleAndEditableBlogs().has_read_permission(request, like.post):
                visible_likes.append(like)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_likes, request)
        serializer = LikeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def list_all(self, request):
        likes = Like.objects.all()
        visible_likes = []

        for like in likes:
            if VisibleAndEditableBlogs().has_read_permission(request, like.post):
                visible_likes.append(like)
        
        visible_likes = sorted(visible_likes, key=lambda like: like.created_at, reverse=True)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(visible_likes, request)
        serializer = LikeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request, post_pk):
        if not request.user.is_authenticated:
            return Response({'error': 'You are not authenticated'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            post = Post.objects.get(pk=post_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if not VisibleAndEditableBlogs().has_read_permission(request, post):
            return Response({'error': 'You do not have permission to like this post'}, status=status.HTTP_403_FORBIDDEN)
        
        if Like.objects.filter(author=request.user, post=post).exists():
            return Response({'error': 'You have already liked this post'}, status=status.HTTP_403_FORBIDDEN)
        
        Like.objects.create(author=request.user, post=post)
        return Response({'success': 'Like created successfully'}, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, post_pk):
        if not request.user.is_authenticated:
            return Response({'error': 'You are not authenticated'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            post = Post.objects.get(pk=post_pk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not VisibleAndEditableBlogs().has_read_permission(request, post):
            return Response({'error': 'You do not have permission to unlike this post'}, status=status.HTTP_403_FORBIDDEN)        
        
        try:
            like = Like.objects.get(author=request.user, post=post)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({'success': 'Like deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
