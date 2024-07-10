from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# 헬퍼 클래스
class UserManager(BaseUserManager):
    def create_user(self, id, password, name, email):
        if not id:
            raise ValueError('Users must have an ID')
        if not password:
            raise ValueError('Users must have a password')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            id=id,
            name=name,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, password, name, email):
        user = self.create_user(
            id=id,
            password=password,
            name=name,
            email=self.normalize_email(email)
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save(using=self._db)
        return user


# AbstractBaseUser를 상속해서 유저 커스텀
class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=255, unique=True, null=False, blank=False, primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255, null=False, blank=False)
    is_deleted = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 헬퍼 클래스 사용
    objects = UserManager()

    # 사용자의 username field는 id로 설정 (아이디로 로그인)
    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return self.id
