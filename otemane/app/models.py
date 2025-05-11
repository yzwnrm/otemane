import uuid
from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin,
    User, 
)
from django.utils import timezone
from django.urls import reverse_lazy


RELATIONSHIP_CHOICES = [
        (0, '母'),
        (1, '父'),
        (2, '祖母'),
        (3, '祖父'),
        (4, '兄'),
        (5, '姉'),
        (6, 'その他'),
    ]

ICON_CHOICES = [
    ("👦", "👦"),
    ("👧", "👧"),
    ("🚗","🚗"),
    ("🎀", "🎀"),
    ("⭐", "⭐"),
]

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Family(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(AbstractBaseUser, PermissionsMixin):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=64)
    relationship = models.IntegerField(choices=RELATIONSHIP_CHOICES, default=6)
    email = models.EmailField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    password = models.CharField(max_length=100)  
    password_token = models.CharField(max_length=100, blank=True, null=True)
    password_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    objects = UserManager()
    
    def __str__(self):
        return self.user_name


class Children(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='children')
    child_name = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=True)
    icon = models.CharField(max_length=10, choices=ICON_CHOICES, default="⭐")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child_name}({self.family})"

class Helps(models.Model):
    child = models.ForeignKey(Children, null=True, blank=True, on_delete=models.CASCADE, related_name='helps')
    help_name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.help_name} "


class Invitation(models.Model):
    STATUS_CHOICES = [
        (0, '保留'),
        (1, '承認'),
        (2, '否認'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, default=1)
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

class HelpLists(models.Model):
    child = models.ForeignKey(Children, on_delete=models.CASCADE)
    help = models.ForeignKey(Helps, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Rewards(models.Model):
    REWARD_CHOICES = [
        (0, 'おかし'),
        (1, 'おかね'),
        (2, 'おねがい'),
    ]

    help = models.ForeignKey(Helps, on_delete=models.CASCADE, related_name='rewards')
    reward_type = models.IntegerField(choices=REWARD_CHOICES, default=0)
    reward_prize = models.IntegerField(null=True, blank=True)
    reward_detail = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reward_detail:
            self.reward_detail = f"{self.get_reward_type_display()} {self.reward_prize or ''}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.get_reward_type_display()} ({self.help})"
    
class Records(models.Model):
    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name='child_helps')
    help = models.ForeignKey(Helps, on_delete=models.CASCADE, related_name='records')
    achievement_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.child.child_name} - {self.help.help_name} ({self.achievement_date})"
    
class Reactions(models.Model):
    REACTION_CHOICES = [
        (0, '💗'), #heart
        (1, '😊'), #smile
        (2, '👍'), #good
        (3, '🌸'), #flower
        (4, '😎'), #nice
    ]

    record = models.ForeignKey(Records, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_image = models.IntegerField(choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
