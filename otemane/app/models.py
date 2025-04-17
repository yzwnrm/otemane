import uuid
from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractUser, PermissionsMixin,
    User, 
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Children(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='children')
    child_name = models.CharField(max_length=100, default='No Name')
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child_name}({self.family})"

class Helps(models.Model):
    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name='helps')
    help_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.help_name} ({self.child.name})"


class Invitation(models.Model):
    STATUS_CHOICES = [
        (0, '保留'),
        (1, '承認'),
        (2, '否認'),
    ]

    family_id = models.IntegerField()
    invitation_URL = models.CharField(max_length=64, unique=True, editable=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invitation_URL:
            self.invitation_URL = uuid.uuid4().hex  # 招待URLトークン生成
        super().save(*args, **kwargs)

    def get_invite_url(self):
        return f'/invite/accept/{self.invitation_URL}/'
