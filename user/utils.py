import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from user.models import User
from user.serializers import RegisterSerializer

# 사용자 ID 반환
def get_user_id_from_token(request):
    try:
        access = request.COOKIES.get('access')
        if not access:
            return JsonResponse({"message": "No access token provided"}, status=401)

        payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return JsonResponse({"message": "Invalid token"}, status=401)

        return user_id

    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Token has expired"}, status=401)

    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Invalid token"}, status=401)

# 사용자 객체 반환
def get_user_from_token(request):
    try:
        access = request.COOKIES.get('access')
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