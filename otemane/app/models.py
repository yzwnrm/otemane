from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractUser, PermissionsMixin,
    User, 
)
from django.urls import reverse_lazy
import uuid

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
    
class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy("accounts:home")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.username} のプロフィール'  

class PasswordResetToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_token',
    )
    token = models.UUIDField(default=uuid.uuid4, db_index=True)
    used = models.BooleanField(default=False)

class Family(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Childmember(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, default='No Name')
    birthday = models.DateField()

