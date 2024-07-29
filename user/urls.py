from django.urls import path
from .views import *

urlpatterns = [
    path('login', AuthLoginView.as_view(), name='login'),  # 로그인
    path('logout', AuthLogoutView.as_view(), name='logout'),  # 로그아웃
    path('register', RegisterAPIView.as_view(), name='register'),  # 회원가입
    #path('user-id-from-token', UserIDFromTokenView.as_view(), name='user_id_from_token'), # 테스트 url
    #path('user-from-token', UserFromTokenView.as_view(), name='user_from_token'), # 테스트 url
]