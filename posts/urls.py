from django.urls import path

from .viewsets import PostViewset , CommentViewset, LikeViewset

urlpatterns = [
    path('post/', PostViewset.as_view({'post': 'create', 'get': 'list'}), name='posts'), # post request to create a post and get request to list all posts
    path('post/<int:pk>/', PostViewset.as_view({'get': 'retrieve', 'put': 'update' , 'delete': 'destroy'}), name='detailed_post'), # get request to retrieve a post, put request to update a post and delete request to delete a post

    path('post/<int:post_pk>/comments/', CommentViewset.as_view({'post': 'create', 'get': 'list_posts'}), name='comments'), # post request to create a comment and get request to list all post's comments
    path('comment/<int:pk>/', CommentViewset.as_view({'delete': 'destroy', 'put': 'update'}), name='comment'), # delete request to delete a comment and put request to update a comment
    path('comment/', CommentViewset.as_view({'get':'list_all'}), name='all_comments'), # get request to list all visible comments
    path('comment/user/<int:user_pk>/', CommentViewset.as_view({'get':'retrieve_users'}), name='specific_user_comments'), # get request to list all visible comments of a specific user

    path('post/<int:post_pk>/likes/', LikeViewset.as_view({'post': 'create', 'get': 'list_posts'}), name='likes'), # post request to like a post and get request to list all post's likes
    path('like/<int:pk>/', LikeViewset.as_view({'delete': 'destroy'}), name='unlike'), # delete request to unlike a post and get request to retrieve a like
    path('like/', LikeViewset.as_view({'get': 'list_all'}), name='all_likes'), # get request to list all likes
    path('likes/user/<int:user_pk>/', LikeViewset.as_view({'get': 'retrieve_users'}), name='specific_user_likes'), # get request to list all likes of a specific user
]
