from rest_framework.views import APIView

from rest_framework import status
import json
from .models import *
from rest_framework.response import Response
from .serializer import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SignupView(APIView):
    @swagger_auto_schema(
        request_body=UserCreateSerializer,
        responses={
            201: UserSerializer,
            400: 'Bad Request'
        },
        tags = ['회원 관련'],
        operation_description="Create a new user account."
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Save the user instance
            user_serializer = UserSerializer(user)  # Use UserSerializer to serialize the user instance

            return Response(user_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriesView(APIView):
    @swagger_auto_schema(
        tags=['카테고리 관련'],
    )
    def get(self, request):
        categories = Category.objects.all().values()
        return Response(list(categories), safe=False, status=status.HTTP_200_OK)

class ChannelCreateView(APIView):
    @swagger_auto_schema(
        tags=['채널 관련'],
    )
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
    @swagger_auto_schema(
        tags=['채널 관련'],
    )
    def post(self, request, channel_id):
        try:
            data = json.loads(request.body)
            message = data.get('message')
            # 여기에 메시지 저장 로직을 추가하세요
            return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChannelResultsView(APIView):
    @swagger_auto_schema(
        tags=['채널 관련'],
    )
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        # 여기에 채널 결과를 반환하는 로직을 추가하세요
        return Response({'results': 'Results for channel {}'.format(channel_id)}, status=status.HTTP_200_OK)

#----------------------------------------------------------------------------------------------------------------------------#

class PostCreateView(APIView):
    @swagger_auto_schema(
        tags=['게시판 관련'],
    )
    def post(self, request):
        try:
            data = json.loads(request.body)
            host_id = data.get('user_id')
            user = User.objects.get(id=host_id)
            post = Post.objects.create(
                host_id=user,
                title=data['title'],
                content=data['content']
            )
            return Response({'post_id': post.id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#----------------------------------------------------------------------------------------------------------------------------#
# 조회 방법 - 모든 게시판 조회

class AllPostGetView(APIView):
    @swagger_auto_schema(
        responses={
            200: PostSerializer,
            400: 'Bad Request'
        },
        tags=['게시판 관련'],
    )
    def get(self, request):
        posts = Post.undeleted_objects.all()

        # 필터링된 쿼리셋을 PostSerializer를 사용하여 직렬화합니다.
        serializer = PostSerializer(posts, many=True)

        # 직렬화된 데이터를 JSON 형태로 응답합니다.
        return Response(serializer.data, status=status.HTTP_200_OK)

# 특정 유저의 게시판 조회
class UserPostsGetView(APIView):
    @swagger_auto_schema(
        responses={
            200: PostSerializer,
            405: 'Not found'
        },
        tags=['게시판 관련'],
    )
    def get(self, request, user_id):
        try:
            # get_queryset 메서드를 호출하여 필터링된 쿼리셋을 가져옵니다.
            user_posts = Post.undeleted_objects.filter(host=user_id)

            # 필터링된 게시물을 PostSerializer를 사용하여 직렬화합니다.
            serializer = PostSerializer(user_posts, many=True)

            # 직렬화된 데이터를 JSON 형태로 응답합니다.
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'User does not have any posts.'}, status=status.HTTP_404_NOT_FOUND)
#----------------------------------------------------------------------------------------------------------------------------#


class PostUpdateView(APIView):
    @swagger_auto_schema(
        tags=['게시판 관련'],
    )
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
    @swagger_auto_schema(
        tags=['게시판 관련'],
    )
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
    @swagger_auto_schema(
        tags=['게시판 관련'],
    )
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
