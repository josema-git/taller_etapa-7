from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer
# Create your views here.

class RegisterView(APIView):
    allowed_methods = ['POST']
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    allowed_methods = ['POST']
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username = serializer.validated_data['username'],
            password = serializer.validated_data['password']
        )

        if user:
            login(request, user)

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):
    allowed_methods = ['POST']
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('refresh')

        if token:
            try:
                token = RefreshToken(token)
                token.blacklist()
            except:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)