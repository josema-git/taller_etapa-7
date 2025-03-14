from rest_framework import viewsets
from rest_framework import status
from django.contrib.auth.models import Group
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate

from .models import User
from .serializers import UserSerializer

# Create your views here.

class UserRegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        team_name = request.data.get('group_name', 'default_group')
        if team_name == '': team_name = 'default_group'
        if User.objects.filter(username=username).exists():
            return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        team, _ = Group.objects.get_or_create(name=team_name)
        if username == '' or password == '':
            return Response({'message': 'Username and password cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password, group_name=team_name)
        user.groups.add(team)
        return Response({'message': 'User created'}, status=status.HTTP_201_CREATED)

class UserLoginView(viewsets.ModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return Response({'message': 'Login successful', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'message': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(viewsets.ModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)