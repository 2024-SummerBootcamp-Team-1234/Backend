from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            id=validated_data['id'],
            name=validated_data['name'],
            email=validated_data.get('email', None),
            password=validated_data['password']
        )

class LoginSerializer(serializers.Serializer):
    id = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        id = data.get('id')
        password = data.get('password')

        if id and password:
            user = authenticate(request=self.context.get('request'), id=id, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Both "id" and "password" are required.')

        data['user'] = user
        return data
