from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class RefreshTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access')
        refresh_token = request.COOKIES.get('refresh')

        if access_token:
            try:
                # 액세스 토큰의 유효성을 검사합니다.
                AccessToken(access_token)
            except Exception as e:
                # 액세스 토큰이 유효하지 않은 경우
                if refresh_token:
                    try:
                        # 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다.
                        new_token = RefreshToken(refresh_token).access_token
                        # 새로운 액세스 토큰을 쿠키에 저장합니다.
                        request.COOKIES['access'] = str(new_token)
                    except Exception as e:
                        # 리프레시 토큰이 유효하지 않은 경우 에러를 반환합니다.
                        return Response({"error": "Invalid refresh token"}, status=401)
                else:
                    # 리프레시 토큰이 없는 경우 에러를 반환합니다.
                    return Response({"error": "Access token expired and no refresh token provided"}, status=401)
        elif not access_token and not refresh_token:
            # 토큰이 없는 경우 미들웨어를 무시하고 계속 진행합니다.
            return self.get_response(request)

        # 토큰이 유효한 경우 요청을 계속 처리합니다.
        response = self.get_response(request)

        # 새로운 액세스 토큰이 발급된 경우 응답에 쿠키를 설정합니다.
        if 'access' in request.COOKIES:
            response.set_cookie('access', request.COOKIES['access'], httponly=True)

        return response
