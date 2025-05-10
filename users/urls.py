from django.urls import path
from .viewsets import UserRegisterView, UserLogoutView, UserViewset
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('register/', UserRegisterView.as_view({'post': 'create'}), name='register'),
    path('logout/', UserLogoutView.as_view({'post': 'create'}), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserViewset.as_view({'get': 'list'}), name='user'),
]