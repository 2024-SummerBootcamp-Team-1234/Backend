import traceback

from django.shortcuts import render, redirect
from django.conf import settings
from accounts.models import User
from allauth.socialaccount.models import SocialAccount, SocialApp
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
import requests
from rest_framework import status
from json.decoder import JSONDecodeError
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.account.utils import perform_login
from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp, SocialAccount

state = getattr(settings, 'STATE')
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/callback/'
def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    client_secret = settings.SOCIAL_AUTH_GOOGLE_SECRET
    code = request.GET.get('code')

    """
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    access_token = token_req_json.get('access_token')

    """
    Email Request
    """
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')

    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User(email=email)
        user.set_unusable_password()
        user.save()

    # SocialAccount 객체 생성 또는 가져오기
    try:
        social_account = SocialAccount.objects.get(user=user, provider='google')
    except SocialAccount.DoesNotExist:
        social_account = SocialAccount(user=user, uid=email_req_json.get('user_id'), provider='google')
        social_account.save()

    # SocialToken 객체 생성 또는 업데이트
    app = SocialApp.objects.get(provider='google')
    try:
        token = SocialToken.objects.get(account=social_account, app=app)
        token.token = access_token
        token.save()
    except SocialToken.DoesNotExist:
        token = SocialToken(token=access_token, app=app, account=social_account)
        token.save()

    # SocialLogin 객체 생성
    social_login = SocialLogin(token=token, account=social_account, user=user)

    # 소셜 로그인 완료
    # 소셜 로그인 완료
    try:
        adapter = get_adapter(request)
        social_login.state = SocialLogin.state_from_request(request)

        if social_login.is_existing:
            # 기존 사용자일 경우 직접 로그인 처리
            perform_login(request, social_login.user, email_verification=settings.ACCOUNT_EMAIL_VERIFICATION)
        else:
            # 새로운 사용자일 경우 소셜 로그인 완료
            complete_social_login(request, social_login)

        return JsonResponse({
            'msg': 'login successful',
            'access_token': access_token,
            'email': email
        })

    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error: {error_message}")
        print(f"Traceback: {error_traceback}")
        return JsonResponse({'error': error_message, 'traceback': error_traceback},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client