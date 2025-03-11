from django.urls import path
from rest_framework import routers
from .viewsets import UserRegisterView, UserLoginView, UserLogoutView

router = routers.DefaultRouter()
router.register('register', UserRegisterView, basename='register')
router.register('login', UserLoginView, basename='login')
router.register('logout', UserLogoutView, basename='logout')

urlpatterns = router.urls
