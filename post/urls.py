from django.urls import path
from .views import *

urlpatterns = [
    path('', PostCreateView.as_view(), name='post_create'),
    path('<int:post_id>/', PostUpdateView.as_view(), name='post_update'),
    path('votes/<int:post_id>/', PostVoteView.as_view(), name='post_vote'),
    path('<int:post_id>', PostDeleteView.as_view(), name='post_delete'),
    # path('<int:post_id>/detail/', PostDetailView.as_view(), name='post_detail'),

    path('all/', AllPostGetView.as_view(), name='get_all_post'),
    path('users/', UserPostsGetView.as_view(), name='get_user_post'),
]