from django import forms
from app.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Children, User, RELATIONSHIP_CHOICES

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
        (0, '母'),
        (1, '父'),
        (2, '祖母'),
        (3, '祖父'),
        (4, '兄'),
        (5, '姉'),
        (6, 'その他'),
    ]
    relationship = forms.ChoiceField(choices=RELATIONSHIP_CHOICES, required=True, label='続柄')

    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワード（再入力）', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'relationship']
        

class UserUpdateForm(forms.ModelForm):
    relationship = forms.ChoiceField(choices=RELATIONSHIP_CHOICES, label='続柄')

    class Meta:
        model = User
        fields = ['username', 'email', 'relationship']
        labels = {
            'username': '名前',
            'email': 'メールアドレス',
            'relationship': '続柄',

        }

class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = ['child_name', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'child_name': 'なまえ',
            'birthday': 'たんじょうび',
        }