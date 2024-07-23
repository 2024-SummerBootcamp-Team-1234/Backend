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
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

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
            return Response({"error": "Text parameter is required"}, status=400)

        audio_data, error = text_to_speach(text)

        if error is None:
            response = HttpResponse(audio_data, content_type='audio/mpeg')
            response['Content-Disposition'] = 'attachment; filename="tts.mp3"'
            return response
        else:
            return Response({"error": f"Error Code: {error}"}, status=500)





# 가상으로 설정한 메시지
virtual_message = ("Hello, this is a virtual message."
                   "Hello, this is a virtual message.")

class SSEAPIView(APIView):

    @swagger_auto_schema(
        tags=['채널'],
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
        tags=['채널'],
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


class SSEAPIView3(APIView):

    @swagger_auto_schema(
        tags=['채널'],
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
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    buffer += content
                    while '.' in buffer:
                        sentence, buffer = buffer.split('.', 1)
                        sentence = sentence.strip()
                        if sentence:
                            data = json.dumps({"content": sentence + '.'})
                            yield f'data: {data}\n\n'

            # Flush any remaining content in the buffer as a final sentence
            if buffer.strip():
                data = json.dumps({"content": buffer.strip()})
                yield f'data: {data}\n\n'

            # for chunk in stream:
            #     if chunk.choices[0].delta.content is not None:
            #         data = json.dumps({"content": chunk.choices[0].delta.content})
            #         yield f'data: {data}\n\n'

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
        response['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the data
        return response