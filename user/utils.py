import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from user.models import User
from user.serializers import RegisterSerializer

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
            return None, JsonResponse({"message": "No access token provided"}, status=401)

        payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return None, JsonResponse({"message": "Invalid token"}, status=401)

        return user_id, None

    except jwt.ExpiredSignatureError:
        return None, JsonResponse({"message": "Token has expired"}, status=401)

    except jwt.InvalidTokenError:
        return None, JsonResponse({"message": "Invalid token"}, status=401)

# 사용자 객체 반환
def get_user_from_token(request):
    try:
        # access = request.COOKIES.get('access') # 원래 코드
        access = get_token_from_request(request) # 스웨거 테스트를 위한 코드
        if not access:
            return JsonResponse({"message": "No access token provided"}, status=401)

        payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return JsonResponse({"message": "Invalid token"}, status=401)

        user = get_object_or_404(User, pk=user_id)
        serializer = RegisterSerializer(user)
        return serializer.data

    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Token has expired"}, status=401)

    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Invalid token"}, status=401)