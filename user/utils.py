import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from user.models import User
from user.serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status


#스웨거 테스트를 위한 함수
# 요청에서 토큰 추출 함수
def get_token_from_request(request):
    # 쿠키에서 토큰 가져오기
    access = request.COOKIES.get('access')

    # 헤더에서 토큰 가져오기
    if not access:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access = auth_header.split(' ')[1]

    return access

# 사용자 ID 반환
def get_user_id_from_token(request):
    try:
        # access = request.COOKIES.get('access') # 원래 코드
        access = get_token_from_request(request) # 스웨거 테스트를 위한 코드
        if not access:
            return None, Response({"message": "No access token provided"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return None,  Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return user_id, None

    except jwt.ExpiredSignatureError:
        return None, Response({"message": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)

    except jwt.InvalidTokenError:
        return None, Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

# 사용자 객체 반환
def get_user_from_token(request):
    try:
        # access = request.COOKIES.get('access') # 원래 코드
        access = get_token_from_request(request) # 스웨거 테스트를 위한 코드
        if not access:
            return Response({"message": "No access token provided"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, pk=user_id)
        serializer = RegisterSerializer(user)
        return serializer.data

    except jwt.ExpiredSignatureError:
        return Response({"message": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)

    except jwt.InvalidTokenError:
        return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)