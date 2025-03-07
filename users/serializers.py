from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import status

from .models import Blogger


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    team = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 're-password' , 'team']

    def validate(self, data):
        if data['password'] != data['re-password']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        return data
    
    def create(self, validated_data):
        team_name = validated_data.pop('team', 'default_team')

        try:
            user = User.objects.create_user(
                username = validated_data['username'],
                password = validated_data['password']
            )

            team = Group.objects.get_or_create(name=team_name)
            Blogger.objects.create(user=user, team=team)
            token = Token.objects.create(user=user)
        except IntegrityError:
            raise serializers.ValidationError({'error': 'User creation failed'})

        return Response({'message': 'User created successfully', 'token': token.key}, status=status.HTTP_201_CREATED)
        
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField() 
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        
        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError({'error': 'Invalid credentials'})
        return data
