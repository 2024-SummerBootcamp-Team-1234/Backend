from django.urls import path
from .views import *

urlpatterns = [
    path('auth/', AuthAPIView.as_view(), name='auth'),  # 정보 조회, 회원가입, 로그아웃
    path('register/', RegisterAPIView.as_view(), name='register'),  # 회원가입
]