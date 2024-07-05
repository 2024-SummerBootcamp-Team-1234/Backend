from django.db import models

class SoftDeletionModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.save()
    class Meta:
        abstract = True

class User(models.Model):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Post(models.Model):
    host_id = models.ForeignKey(User, db_constraint=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    vote = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

class LikePost(models.Model):
    id = models.IntegerField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_constraint=True)
    user_id = models.CharField(max_length=255)
    is_deleted = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Channel(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=True)
    is_deleted = models.BooleanField(null=True, default=False)
    message = models.TextField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

class Post_Category(models.Model):
    post_id = models.ForeignKey(Post, db_constraint=False)
    category_id = models.ForeignKey(Category, db_constraint=False)
    is_deleted = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

