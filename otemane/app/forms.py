from django import forms
from app.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()
# class RegistForm(forms.ModelForm):

#     class Meta:
#         model = User
#         fields = ['username', 
#                 #   'relationship', 
#                   'email', 'password']
#         widgets = {
#             'password': forms.PasswordInput(),
#         }
#         labels = {
#             'username': '名前/ニックネーム',
#             # 'relationship': '続柄',
#             'email': 'メールアドレス',
#             'password': 'パスワード',    
#         }

#     def save(self, commit = False):
#         user = super().save(commit=False)
#         validate_password(self.cleaned_data['password'], user)
#         user.set_password(self.cleaned_data['password'])
#         user.save()
#         return user

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label='名前/ニックネーム')
    email = forms.EmailField(required=True, label='メールアドレス')
    
    RELATIONSHIP_CHOICES = [
        ('mother', '母'),
        ('father', '父'),
        ('sisiter', '姉'),
        ('brother', '兄'),
        ('graundmother', '祖母'),
        ('graundfather', '祖父'),
        ('other', 'その他'),
    ]
    relationship = forms.ChoiceField(choices=RELATIONSHIP_CHOICES, required=True, label='続柄')
    
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワード（再入力）', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'relationship']

class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput()
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError('このメールアドレスのユーザーは存在しません')
        return email
    
class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput,
    )

    password2 = forms.CharField(
        label='新しいパスワード(確認)',
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_date = super().clean()
        password1 =cleaned_date.get('password1')
        password2 =cleaned_date.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('パスワードが一致しません')
            else:
                raise ValidationError('パスワードを設定してください')
            return cleaned_date
            
# class UserChangeForm(UserChangeForm):

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': '名前',
            'email': 'メールアドレス',
        }


class UserProfileForm(forms.ModelForm):

    RELATIONSHIP_CHOICES = [
        ('mother', '母'),
        ('father', '父'),
        ('sister', '姉'),
        ('brother', '兄'),
        ('grandmother', '祖母'),
        ('grandfather', '祖父'),
        ('other', 'その他'),
    ]
    
    relationship = forms.ChoiceField(
        choices=RELATIONSHIP_CHOICES,
        required=True,
        label='続柄',
        initial='other',  # デフォルトで「その他」を選択
    )

    class Meta:
        model = UserProfile
        fields = ['relationship']