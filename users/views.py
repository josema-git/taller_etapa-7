from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from .serializers import RegisterSerializer, LoginSerializer
# Create your views here.

class RegisterView(APIView):
    allowed_methods = ['POST']
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

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

            return Response({
                'message': 'Login successful',
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):
    allowed_methods = ['POST']
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)