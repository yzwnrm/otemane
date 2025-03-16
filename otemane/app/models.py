from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy


class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        if not password:
            raise ValueError('パスワードを入力してください')
        user = self.model(
            username=username,
            email=self.normalaze_email(email)
        )
        user.set_password(password)
        user.save()
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy("accounts:home")
    