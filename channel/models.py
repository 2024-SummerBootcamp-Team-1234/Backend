from django.db import models
from user.models import User

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


class Channel(SoftDeletionModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_constraint=False)
    message = models.TextField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
