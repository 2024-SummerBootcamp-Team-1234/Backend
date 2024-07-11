from django.urls import path
from .views import *

urlpatterns = [
    path('channels/', ChannelCreateView.as_view(), name='channel_create'),
    path('channels/messages/<int:channel_id>/', SendMessageView.as_view(), name='send_message'),
    path('channels/results/', ChannelResultsView.as_view(), name='channel_results'),

    path('posts/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:post_id>/', PostUpdateView.as_view(), name='post_update'),
    path('posts/votes/<int:post_id>/', PostVoteView.as_view(), name='post_vote'),
    path('posts/<int:post_id>', PostDeleteView.as_view(), name='post_delete'),
    # path('posts/<int:post_id>/detail/', PostDetailView.as_view(), name='post_detail'),

    path('posts/all/', AllPostGetView.as_view(), name='get_all_post'),
    path('posts/users/', UserPostsGetView.as_view(), name='get_user_post'),
]