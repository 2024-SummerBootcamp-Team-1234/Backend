from rest_framework.views import APIView

from rest_framework import status
import json
from .models import *
from rest_framework.response import Response
from .serializer import *


class SignupView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Save the user instance
            user_serializer = UserSerializer(user)  # Use UserSerializer to serialize the user instance

            return Response(user_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriesView(APIView):
    def get(self, request):
        categories = Category.objects.all().values()
        return Response(list(categories), safe=False, status=status.HTTP_200_OK)

class ChannelCreateView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            channel = Channel.objects.create(user_id=user)
            return Response({'channel_id': channel.id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SendMessageView(APIView):
    def post(self, request, channel_id):
        try:
            data = json.loads(request.body)
            message = data.get('message')
            # 여기에 메시지 저장 로직을 추가하세요
            return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChannelResultsView(APIView):
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        # 여기에 채널 결과를 반환하는 로직을 추가하세요
        return Response({'results': 'Results for channel {}'.format(channel_id)}, status=status.HTTP_200_OK)


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
            return Response({'post_id': post.id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostUpdateView(APIView):
    def put(self, request, post_id):
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=post_id)
            post.title = data.get('title', post.title)
            post.content = data.get('content', post.content)
            post.save()
            return Response({'message': 'Post updated successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostVoteView(APIView):
    def put(self, request, post_id):
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=post_id)
            input_value = data.get('input', 1)
            post.vote += input_value
            post.save()
            return Response({'message': 'Post vote updated successfully'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


#----------------------------------------------------------------------------------------------------------------------------#
# 소프트 삭제 구현 방법
class PostDeleteView(APIView):
    def delete(self, request, post_id):
        try:
            # 게시물 조회
            post = Post.objects.get(pk=post_id)

            # 소프트 삭제 수행
            post.soft_delete()

            return Response({"message": "게시물이 성공적으로 삭제되었습니다."})

        except Post.DoesNotExist:
            return Response({"error": "삭제할 게시물을 찾을 수 없습니다."},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#----------------------------------------------------------------------------------------------------------------------------#
