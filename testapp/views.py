from rest_framework.views import APIView
from rest_framework import status
import json
from .models import *
from rest_framework.response import Response
from .serializer import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category
from .serializer import CategorySerializer

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

# 삭제된 카테고리 제외하고 전체 불러오기
class CategoriesView(APIView):
    @swagger_auto_schema(
        tags=['카테고리 관련'],
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request):
        categories = Category.undeleted_objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#-----------------------------------------------------------------------------------#
class ChannelCreateView(APIView):
    @swagger_auto_schema(
        tags=['채널 관련'],
        request_body=ChannelCreateSerializer,
        responses={201: ChannelSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = ChannelCreateSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                user = User.objects.get(id=user_id)
                channel = Channel.objects.create(user=user)
                channel_serializer = ChannelSerializer(channel)
                return Response(channel_serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({'error': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#-----------------------------------------------------------------------------------#

class SendMessageView(APIView):
    @swagger_auto_schema(
        tags=['채널 관련'],
        request_body=ChannelSerializer,  # Assuming you want to use the same serializer
    )
    def post(self, request, channel_id):
        try:
            data = json.loads(request.body)
            message = data.get('message')
            channel = Channel.objects.get(id=channel_id)
            channel.message = message
            channel.save()
            return Response({'message': '메시지가 성공적으로 전송되었습니다.'}, status=status.HTTP_201_CREATED)
        except Channel.DoesNotExist:
            return Response({'error': '채널을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChannelResultsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('channel_id', openapi.IN_QUERY, description="Channel ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        try:   
            channel = Channel.objects.get(id=channel_id)
            serializer = ChannelSerializer(channel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Channel.DoesNotExist:
            return Response({'error': '채널을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

#----------------------------------------------------------------------------------------------------------------------------#

class PostCreateView(APIView):
    @swagger_auto_schema(
        tags=['게시판 관련'],
        request_body=PostCreateSerializer,
        responses={201: PostSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=serializer.validated_data['host'].id)
                post = serializer.save(host=user)
                post_serializer = PostSerializer(post)
                return Response(post_serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({'error': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
        serializer = PostSerializer(posts, many=True)
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
            user_posts = Post.undeleted_objects.filter(host=user_id)
            serializer = PostSerializer(user_posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': '게시물이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
#----------------------------------------------------------------------------------------------------------------------------#


class PostUpdateView(APIView):
    @swagger_auto_schema(
        tags=['게시판 관련'],
        request_body=PostSerializer,
    )
    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': '게시물이 성공적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': '게시물을 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostVoteView(APIView):
    @swagger_auto_schema(
        tags=['게시판 관련'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'input': openapi.Schema(type=openapi.TYPE_INTEGER, description='Vote increment/decrement')
            }
        ),
    )
    def put(self, request, post_id):
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=post_id)
            input_value = data.get('input', 1)
            post.vote += input_value
            post.save()
            return Response({'message': '게시물 투표가 완료되었습니다.'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': '게시물을 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
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
            post = Post.objects.get(pk=post_id)
            post.soft_delete()
            return Response({"message": "게시물이 성공적으로 삭제되었습니다."})
        except Post.DoesNotExist:
            return Response({"error": "삭제할 게시물을 찾을 수 없습니다."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#----------------------------------------------------------------------------------------------------------------------------#
