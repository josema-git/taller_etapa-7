from django.urls import path

from .viewsets import PostViewset , CommentViewset, LikeViewset

urlpatterns = [
    path('post/', PostViewset.as_view({'post': 'create', 'get': 'list'}), name='posts'),
    path('post/<int:pk>/', PostViewset.as_view({'get': 'retrieve', 'put': 'update' , 'delete': 'destroy'}), name='detailed_post'),
    path('post/<int:post_pk>/comments/', CommentViewset.as_view({'post': 'create', 'get': 'list'}), name='comments'),
    path('comment/<int:pk>/', CommentViewset.as_view({'delete': 'destroy', 'put': 'update'}), name='comment'),

    path('comment/', CommentViewset.as_view({'get':'list_all'}), name='all_comments'),
    path('comment/<int:user_pk>/', CommentViewset.as_view({'get':'retrieve_users'}), name='specific_user_comments'),

    path('post/<int:post_pk>/likes/', LikeViewset.as_view({'post': 'create', 'get': 'list_posts'}), name='likes'),
    path('like/<int:pk>/', LikeViewset.as_view({'delete': 'destroy', 'get': 'retrieve'}), name='unlike'),

    path('like/', LikeViewset.as_view({'get': 'list_all'}), name='all_likes'),
    path('like/<int:user_pk>/', LikeViewset.as_view({'get': 'retrieve_users'}), name='specific_user_likes'),
]
