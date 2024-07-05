from django.db import models

class SoftDeleteManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SoftDeletionModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    objects = models.Manager()
    undeleted_objects = SoftDeleteManager()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):  # 삭제된 레코드를 복구한다.
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])

    class Meta:
        abstract = True


class User(SoftDeletionModel):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Post(SoftDeletionModel):
    host = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, db_constraint=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    vote = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Category(SoftDeletionModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class LikePost(SoftDeletionModel):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, db_constraint=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Channel(SoftDeletionModel):
    id = models.AutoField(primary_key=True)
    user= models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_constraint=False)
    message = models.TextField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)


class Post_Category(SoftDeletionModel):
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, db_constraint=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


