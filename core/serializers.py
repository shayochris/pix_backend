from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','email']

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model=Test
        fields="__all__"

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields="__all__"

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields="__all__"
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields="__all__"