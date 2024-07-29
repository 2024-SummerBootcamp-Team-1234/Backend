import base64

from rest_framework import status
from django.http import HttpResponse
import json
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import openai as openai
from user.utils import *
from .utils import *
import time
from user.utils import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
from dotenv import load_dotenv


load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")

class TTSView(APIView):
    @swagger_auto_schema(
        tags=['channel'],
        manual_parameters=[
            openapi.Parameter('text', openapi.IN_QUERY, description="Text to convert to speech", type=openapi.TYPE_STRING, required=True)
        ]
    )
    def get(self, request):
        text = request.GET.get('text')
        if not text:
            return Response({"error": "Text parameter is required"}, status=400)

        audio_data, error = text_to_speech(text)

        if error is None:
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            return JsonResponse({"audio_data": encoded_audio})
        else:
            return Response({"error": f"Error Code: {error}"}, status=500)

class ChannelCreateView(APIView):
    @swagger_auto_schema(
        tags=['channel'],
        responses={201: ChannelCreateSerializer, 400: 'Bad Request'}
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
# 가상으로 설정한 메시지
virtual_message = ("Hello, this is a virtual message."
                   "Hello, this is a virtual message.")

class SSEAPIView(APIView):

    @swagger_auto_schema(
        tags=['channel'],
        manual_parameters=[
            openapi.Parameter('channel_id', openapi.IN_QUERY, description="Channel ID", type=openapi.TYPE_INTEGER)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message to send')
            },
            required=['message']
        )
    )
    def post(self, request, channel_id):
        # 요청 본문에서 message를 받는 형식만 유지
        message_text = request.data.get('message')
        if message_text is not None:
            def event_stream():
                word = ""
                for char in virtual_message:
                    if char.isspace() or char in (".", ",", "!", "?"):  # 단어 구분자
                        if word:
                            data = json.dumps({"content": word})
                            yield f"data: {data}\n\n"
                            time.sleep(0.25)  # 0.25초 간격으로 단어 전송
                            word = ""
                        if char.isspace():
                            continue
                        else:
                            data = json.dumps({"content": char})
                            yield f"data: {data}\n\n"
                            time.sleep(0.25)  # 0.25초 간격으로 구두점 전송
                    else:
                        word += char

                if word:  # 마지막 단어 처리
                    data = json.dumps({"content": word})
                    yield f"data: {data}\n\n"

            # StreamingHttpResponse를 사용하여 스트림 응답 반환
            # return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
            response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
            response['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
            response['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the data
            response['Content-Language'] = request.headers.get('Accept-Language', 'en')
            return response

        return Response({"error": "Message not provided"}, status=400)


class SSEAPIView2(APIView):

    @swagger_auto_schema(
        tags=['channel'],
        manual_parameters=[
            openapi.Parameter('channel_id', openapi.IN_QUERY, description="Channel ID", type=openapi.TYPE_INTEGER)
        ],
    )
    def get(self, request, channel_id):
        # 요청 본문에서 message를 받는 형식만 유지
        message_text = request.data.get('message')
        if message_text is not None:
            def event_stream():
                for char in virtual_message:
                    # 각 문자를 JSON 형식으로 감쌈
                    data = json.dumps({"content": char})
                    yield f"data: {data}\n\n"
                    time.sleep(0.25)  # 0.25초 간격으로 문자 전송

            # StreamingHttpResponse를 사용하여 스트림 응답 반환
            return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

        return Response({"error": "Message not provided"}, status=400)

# ----------------------------------------------------------------------------------------------------------------------------#

class SSEAPIView3(APIView):

    @swagger_auto_schema(
        tags=['channel'],
        manual_parameters=[
            openapi.Parameter('channel_id', openapi.IN_QUERY, description="Channel ID", type=openapi.TYPE_INTEGER)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message to send')
            },
            required=['message']
        )
    )
    def post(self, request, channel_id):
        message = request.data.get('message', '')

        def event_stream():
            client = openai.OpenAI(api_key=openai.api_key)
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                stream=True
            )
            buffer = ""
            for chunk in stream:
                content = getattr(chunk.choices[0].delta, 'content', None)
                if content is not None:
                    buffer += content
                    data = json.dumps({"content": content})
                    yield f'data: {data}\n\n'

                    if '.' in buffer:
                        sentence, buffer = buffer.split('.', 1)
                        sentence = sentence.strip()
                        if sentence:
                            # 텍스트를 음성으로 변환
                            audio_data, error = text_to_speech(sentence + '.')
                            if audio_data:
                                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                                audio_json = json.dumps({"audio": audio_base64})
                                yield f'data: {audio_json}\n\n'
                            elif error:
                                error_json = json.dumps({"error": f"Error code: {error}"})
                                yield f'data: {error_json}\n\n'

            # 남은 내용을 처리
            if buffer.strip():
                data = json.dumps({"content": buffer.strip()})
                yield f'data: {data}\n\n'

                # 남은 텍스트를 음성으로 변환
                audio_data, error = text_to_speech(buffer.strip())
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    audio_json = json.dumps({"audio": audio_base64})
                    yield f'data: {audio_json}\n\n'
                elif error:
                    error_json = json.dumps({"error": f"Error code: {error}"})
                    yield f'data: {error_json}\n\n'

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['X-Accel-Buffering'] = 'no'  # Nginx 버퍼링 비활성화
        response['Cache-Control'] = 'no-cache'  # 클라이언트가 데이터를 캐시하지 않도록 설정
        return response

#######################################################################################################################
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key
@csrf_exempt
@require_POST
def chat_view(request, channel_id):
    try:
        data = json.loads(request.body)
        message_list = data.get('message')

        message = " ".join(message_list)

        # Generate a response stream for the initial query
        response_stream = generate_initial_response_stream(channel_id, message)
        return StreamingHttpResponse(response_stream, content_type="text/event-stream")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
@require_POST
def chat_followup_view(request, channel_id):
    try:
        data = json.loads(request.body)
        message_list = data.get('message')

        message = " ".join(message_list)

        # Generate a response stream for the follow-up query
        response_stream = generate_followup_response_stream(channel_id, message)
        return StreamingHttpResponse(response_stream, content_type="text/event-stream")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
