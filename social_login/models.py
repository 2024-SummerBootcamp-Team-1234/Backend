from django.db import models
# from django.utils import timezone
#
# class User(models.Model):
#     id = models.CharField(max_length=255, unique=True, primary_key=True)
#     name = models.CharField(max_length=255, null=False)
#     email = models.CharField(max_length=255, null=True)
#     password = models.CharField(max_length=255, null=False)
#     is_deleted = models.BooleanField(null=True, default=False)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(default=timezone.now)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = 'user'
