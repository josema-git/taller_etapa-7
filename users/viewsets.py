from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, UserRetrieveSerializer

# Create your views here.

class UserRegisterView(viewsets.ModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'message': 'username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'message': 'an account with that email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=username, password=password, team='default_team')
        return Response({'message': 'User created succesfully'}, status=status.HTTP_201_CREATED)

class UserLogoutView(viewsets.ModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
        except KeyError:
            return Response({'message': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def list(self, request):
        user = User.objects.filter(id=request.user.id)
        serializer = self.get_serializer(user.first())
        return Response(serializer.data, status=status.HTTP_200_OK)