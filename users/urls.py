from django.urls import path
from .viewsets import UserRegisterView, UserLoginView, UserLogoutView

urlpatterns = [
    path('register/', UserRegisterView.as_view({'post': 'create'}), name='register'),
    path('login/', UserLoginView.as_view({'post': 'create'}), name='login'),
    path('logout/', UserLogoutView.as_view({'post': 'create'}), name='logout'),
]