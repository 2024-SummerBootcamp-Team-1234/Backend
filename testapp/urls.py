from django.urls import path
from .views import SignupView, LoginView, LogoutView, CategoriesView, ChannelCreateView, SendMessageView, ChannelResultsView, PostCreateView, PostUpdateView, PostVoteView, PostDeleteView

urlpatterns = [
    path('users/signup/', SignupView.as_view(), name='user_signup'),
    path('users/login/', LoginView.as_view(), name='user_login'),
    path('users/logout/', LogoutView.as_view(), name='user_logout'),
    path('categories/', CategoriesView.as_view(), name='categories_list'),
    path('channels/', ChannelCreateView.as_view(), name='channel_create'),
    path('channels/messages/<int:channel_id>/', SendMessageView.as_view(), name='send_message'),
    path('channels/results/', ChannelResultsView.as_view(), name='channel_results'),
    path('posts/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:post_id>/', PostUpdateView.as_view(), name='post_update'),
    path('posts/votes/<int:post_id>/', PostVoteView.as_view(), name='post_vote'),
    path('posts/<int:post_id>/', PostDeleteView.as_view(), name='post_delete'),
]
