import jwt
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from .utils import get_user_id_from_token, get_user_from_token
from django.http import JsonResponse
from .models import User
from drf_yasg import openapi

class RegisterAPIView(APIView):

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: 'Bad Request'
        },
        tags=['User'],
        operation_description="Register a new user by providing an ID, name, email, and password."
    )
    #회원가입
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": serializer.data,
                "message": "Register successful"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class AuthAPIView(APIView):
#
#     @swagger_auto_schema(
#         responses={
#             200: RegisterSerializer,
#             401: 'Unauthorized',
#             400: 'Invalid token'
#         },
#         tags=['User'],
#         operation_description="Retrieve user information using the access token in cookies."
#     )
#     # 유저 정보 확인
#     def get(self, request):
#         try:
#             # access token을 decode 해서 유저 id 추출 => 유저 식별
#             access = request.COOKIES.get('access')
#             if not access:
#                 return Response({"message": "No access token provided"}, status=status.HTTP_401_UNAUTHORIZED)
#
#             payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
#             pk = payload.get('user_id')
#             user = get_object_or_404(User, pk=pk)
#             serializer = RegisterSerializer(instance=user)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#
#         except jwt.ExpiredSignatureError:
#             # 토큰 만료 시 토큰 갱신
#             data = {'refresh': request.COOKIES.get('refresh', None)}
#             serializer = TokenRefreshSerializer(data=data)
#             if serializer.is_valid(raise_exception=True):
#                 access = serializer.data.get('access', None)
#                 refresh = serializer.data.get('refresh', None)
#                 payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
#                 pk = payload.get('user_id')
#                 user = get_object_or_404(User, pk=pk)
#                 serializer = RegisterSerializer(instance=user)
#                 res = Response(serializer.data, status=status.HTTP_200_OK)
#                 res.set_cookie('access', access)
#                 res.set_cookie('refresh', refresh)
#                 return res
#             return Response({"message": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
#
#         except jwt.InvalidTokenError:
#             # 사용 불가능한 토큰일 때
#             return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class AuthLoginView(APIView):

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    'application/json': {
                        "user": {
                            "id": "example_id",
                            "name": "example_name",
                            "email": "example_email@example.com"
                        },
                        "message": "Login success",
                        "token": {
                            "access": "access_token_example",
                            "refresh": "refresh_token_example"
                        }
                    }
                }
            ),
            400: 'Invalid credentials'
        },
        tags=['User'],
        operation_description="Login user by providing ID and password, returns JWT tokens."
    )
    # 로그인
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            # JWT 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": RegisterSerializer(user).data,
                    "message": "Login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            # JWT 토큰을 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthLogoutView(APIView):

    @swagger_auto_schema(
        responses={
            202: 'Logout success'
        },
        tags=['User'],
        operation_description="Logout user by deleting the JWT tokens in cookies."
    )
    # 로그아웃
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
        response = Response({
            "message": "Logout success"
        }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response

# -----------------------------------------------------------------------------------#
# 테스트를 위한 view
class UserIDFromTokenView(APIView):
    @swagger_auto_schema(
        tags=['Test']
    )
    def get(self, request):
        user_id = get_user_id_from_token(request)
        if isinstance(user_id, JsonResponse):  # If the function returned an error response
            return user_id
        return Response({"user_id": user_id}, status=status.HTTP_200_OK)

class UserFromTokenView(APIView):
    @swagger_auto_schema(
        tags=['Test']
    )
    def get(self, request):
        user_data = get_user_from_token(request)
        if isinstance(user_data, JsonResponse):  # If the function returned an error response
            return user_data
        return Response(user_data, status=status.HTTP_200_OK)