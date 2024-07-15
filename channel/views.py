from rest_framework import status
from django.http import HttpResponse, JsonResponse
import json
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from user.utils import *
from .utils import *
import time
from rest_framework.response import Response
from rest_framework.views import APIView
from myapp.serializers import MessageSerializer

class ChannelCreateView(APIView):
    @swagger_auto_schema(
        tags=['채널'],
        responses={201: ChannelSerializer, 400: 'Bad Request'}
    )
    # 채널 생성
    def post(self, request):
        user_id, error_response = get_user_id_from_token(request)
        if error_response:
            return error_response

        try:
            user = User.objects.get(id=user_id)
            channel = Channel.objects.create(user=user)
            channel_serializer = ChannelCreateSerializer(channel)
            return Response(channel_serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------------------------------------#

class SendMessageView(APIView):
    @swagger_auto_schema(
        tags=['채널'],
        request_body=ChannelSerializer,  # Assuming you want to use the same serializer
    )
    # 메시지 전송
    def post(self, request, channel_id):
        try:
            data = json.loads(request.body)
            message = data.get('message')

            if not channel_id:
                return Response({'error': 'Channel ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            if message is None:
                return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

            channel = Channel.objects.get(id=channel_id)
            channel.message = message
            channel.save()

            # Response에 RAG를 통한 응답을 포함 + channel.message에 응답 내용 추가

            return Response({'message': '메시지가 성공적으로 전송되었습니다.'}, status=status.HTTP_201_CREATED)
        except Channel.DoesNotExist:
            return Response({'error': '채널을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------------------------------------------------------------------------------#

class ChannelResultsView(APIView):
    @swagger_auto_schema(
        tags=['채널'],
        manual_parameters=[
            openapi.Parameter('channel_id', openapi.IN_QUERY, description="Channel ID",
                              type=openapi.TYPE_INTEGER)
        ]
    )
    # 결과 확인
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        try:
            channel = Channel.objects.get(id=channel_id)
            serializer = ChannelSerializer(channel)

            # Response에 RAG를 통한 결과를 포함 + channel.result에 결과 내용 추가

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Channel.DoesNotExist:
            return Response({'error': '채널을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

# ----------------------------------------------------------------------------------------------------------------------------#
# tts 테스트 코드
class TTSView(APIView):
    @swagger_auto_schema(
        tags=['Test'],
        manual_parameters=[
            openapi.Parameter('text', openapi.IN_QUERY, description="Text to convert to speech", type=openapi.TYPE_STRING, required=True)
        ]
    )
    def get(self, request):
        text = request.GET.get('text')
        if not text:
            return JsonResponse({"error": "Text parameter is required"}, status=400)

        audio_data, error = text_to_speach(text)

        if error is None:
            response = HttpResponse(audio_data, content_type='audio/mpeg')
            response['Content-Disposition'] = 'attachment; filename="tts.mp3"'
            return response
        else:
            return JsonResponse({"error": f"Error Code: {error}"}, status=500)





# 가상으로 설정한 메시지
virtual_message = "Hello, this is a virtual message."

class SSEAPIView(APIView):
    serializer_class = MessageSerializer

    @swagger_auto_schema(
        tags=['채널'],
        manual_parameters=[
            openapi.Parameter('channel_id', openapi.IN_QUERY, description="Channel ID",
                              type=openapi.TYPE_INTEGER)
        ],
    )
    def post(self, request, channel_id):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            message_text = serializer.validated_data.get('message')

            def event_stream():
                for char in message_text:
                    yield f"data: {char}\n\n"
                    time.sleep(1)  # 1초 간격으로 문자 전송

            return Response(event_stream(), content_type='text/event-stream')

        return Response(serializer.errors, status=400)