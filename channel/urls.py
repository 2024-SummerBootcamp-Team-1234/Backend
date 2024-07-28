from django.urls import path
from .views import *

urlpatterns = [
    path('', ChannelCreateView.as_view(), name='channel_create'),
    path('results/<int:channel_id>', chat_view, name='chat_view'),
    path('messages/<int:channel_id>', chat_followup_view, name='chat_followup_view'),
    path('tts', TTSView.as_view(), name='tts'),
    path('virtual_messages/<int:channel_id>',SSEAPIView.as_view(), name='virtual_message'),
    path('virtual_messages2/<int:channel_id>',SSEAPIView2.as_view(), name='virtual_message'),
    path('virtual_messages3/<int:channel_id>',SSEAPIView3.as_view(), name='virtual_message'),
]