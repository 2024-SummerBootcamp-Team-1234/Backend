from django.db import models

class User(models.Model):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.DateTimeField(null=True, blank=True)
class Channel(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channels')
    is_deleted = models.DateTimeField(null=True, blank=True)

# 카테고리 모델
class Category(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.DateTimeField(null=True, blank=True)

# 게시판 모델
class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    vote = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.DateTimeField(null=True, blank=True)

# 카테고리_게시판 모델
class CategoryPost(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='category_posts')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_posts')


