from django.urls import path
from .views import *

urlpatterns = [
    path('', ChannelCreateView.as_view(), name='channel_create'),
    path('messages/<int:channel_id>/', SendMessageView.as_view(), name='send_message'),
    path('results/', ChannelResultsView.as_view(), name='channel_results'),
    path('tts/', TTSView.as_view(), name='tts'), # 테스트 url
]