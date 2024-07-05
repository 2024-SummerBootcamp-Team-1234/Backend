from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
import json
from .models import User, Channel, Post, Category
from rest_framework.response import Response
from .serializer import UserCreateSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(method='post', request_body=UserCreateSerializer,
                     responses={201: UserSerializer}, operation_summary="회원 생성", tags=['회원관리'])
class SignupView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = User.objects.get(email=data['email'], password=data['password'])
            return JsonResponse({'user_id': user.id}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid login credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        return JsonResponse({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class CategoriesView(APIView):
    def get(self, request):
        categories = Category.objects.all().values()
        return JsonResponse(list(categories), safe=False, status=status.HTTP_200_OK)

class ChannelCreateView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            channel = Channel.objects.create(user_id=user)
            return JsonResponse({'channel_id': channel.id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SendMessageView(APIView):
    def post(self, request, channel_id):
        try:
            data = json.loads(request.body)
            message = data.get('message')
            # 여기에 메시지 저장 로직을 추가하세요
            return JsonResponse({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChannelResultsView(APIView):
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        # 여기에 채널 결과를 반환하는 로직을 추가하세요
        return JsonResponse({'results': 'Results for channel {}'.format(channel_id)}, status=status.HTTP_200_OK)

class PostCreateView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            post = Post.objects.create(
                user_id=user,
                title=data['title'],
                content=data['content']
            )
            return JsonResponse({'post_id': post.id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostUpdateView(APIView):
    def put(self, request, post_id):
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=post_id)
            post.title = data.get('title', post.title)
            post.content = data.get('content', post.content)
            post.save()
            return JsonResponse({'message': 'Post updated successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostVoteView(APIView):
    def put(self, request, post_id):
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=post_id)
            input_value = data.get('input', 1)
            post.vote += input_value
            post.save()
            return JsonResponse({'message': 'Post vote updated successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostDeleteView(APIView):
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            post.is_deleted = timezone.now()
            post.save()
            return JsonResponse({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
