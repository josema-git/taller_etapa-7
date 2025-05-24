from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'team']
        write_only_fields = ['password']
    
class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
        read_only_fields = ['id', 'username', 'team']
    