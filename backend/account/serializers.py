from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.hashers import make_password



class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'email', 'password')

        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8},
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'email', 'username', 'is_staff')

class AddUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'email','password', 'is_staff')

        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 8},
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['id','user', 'user_type','created_at', 'updated_at']



class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance['password']= make_password(password)
            instance.save()
        return instance

class EditProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ('user', 'user_type')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = EditUserSerializer(instance=instance.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        instance.user_type = validated_data.get('user_type', instance.user_type)
        if instance.user_type == "admin":
            instance.user.is_superuser = True
            instance.user.is_staff = True
        instance.save()
        return instance

