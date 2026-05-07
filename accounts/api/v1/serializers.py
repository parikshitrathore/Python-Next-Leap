from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from accounts.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'date_of_birth', 'address',
                 'state', 'city', 'password', 'confirm_password', 'token']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        user.token = token.key
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return {
                'username': user.username,
                'token': token.key
            }
        raise serializers.ValidationError("Incorrect Credentials")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'date_of_birth',
                 'address', 'state', 'city', 'created_at', 'updated_at']
        read_only_fields = ['username', 'email', 'created_at', 'updated_at']
