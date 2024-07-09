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
    class Meta:
        model = Post
        fields = ['host','title','content']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['host','title','content','vote','created_at']



#--------------------------------------------------------------#

class ChannelCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    class Meta:
        fields = ['user_id']

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'user', 'message', 'result']