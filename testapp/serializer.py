from rest_framework import serializers

from testapp.models import *


#--------------------------------------------------------------#
# User 관련
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email','password']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','password']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name', 'email']

#--------------------------------------------------------------#
# 게시판 관련
class PostCreateSerializer(serializers.ModelSerializer):
    class Mete:
        model = Post
        fields = ['user_id','title','content']



#--------------------------------------------------------------#