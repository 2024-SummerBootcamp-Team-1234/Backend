from django.urls import path
from .views import *

urlpatterns = [
    path('auth/', AuthAPIView.as_view(), name='auth'),  # 정보 조회, 회원가입, 로그아웃
    path('register/', RegisterAPIView.as_view(), name='register'),  # 회원가입
    path('user-id-from-token/', UserIDFromTokenView.as_view(), name='user_id_from_token'), # 테스트 url
    path('user-from-token/', UserFromTokenView.as_view(), name='user_from_token'), # 테스트 url
]