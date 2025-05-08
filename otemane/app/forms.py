from django import forms
from django.forms import modelformset_factory
from app.models import User, Helps
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Children, User, Rewards, RELATIONSHIP_CHOICES, HelpLists, Reactions

User = get_user_model()

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

class UserRegistrationForm(UserCreationForm):
    user_name = forms.CharField(label='名前/ニックネーム')
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
        fields = ['user_name', 'email', 'relationship']
        

class UserUpdateForm(forms.ModelForm):
    relationship = forms.ChoiceField(choices=RELATIONSHIP_CHOICES, label='続柄')
    new_email = forms.EmailField(label='新しいメールアドレス', required=False)

    class Meta:
        model = User
        fields = ['user_name', 'relationship', 'email' ]
        labels = {
            'user_name': '名前/ニックネーム',
            'relationship': '続柄',
            'email': 'メールアドレス'
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_email = self.cleaned_data.get('new_email')

        if new_email:
            user.email = new_email  # 新しいメールアドレスがあれば上書き

        if commit:
            user.save()
        return user


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

    def save(self, commit=True):
        child = super().save(commit=False)
        
        if commit:
            child.save()
        return child

class ChildUpdateForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = ['child_name', 'birthday', 'icon']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'icon': forms.RadioSelect
        }
        labels = {
            'child_name': 'なまえ',
            'birthday': 'たんじょうび',
        }

class HelpsForm(forms.ModelForm):
    class Meta:
        model = Helps
        fields = ['help_name']
        labels = {
            'help_name': '',
        }

        
class RewardsForm(forms.ModelForm):
    class Meta:
        model = Rewards
        fields = ['reward_type', 'reward_prize', 'reward_detail']
        widgets = {
            'reward_type': forms.RadioSelect, 
            'reward_prize': forms.NumberInput(attrs={'placeholder': 'いくら？', 'class': 'form-control'}),
            'reward_detail': forms.TextInput(attrs={'placeholder': 'どんなこと？', 'class': 'form-control'}),
        }

RewardsFormSet = modelformset_factory(
    Rewards,
    form=RewardsForm,
    extra=1,  # 初期フォームを1つ表示
    can_delete=True  # フォームを削除できるオプションを追加
)

class PasswordConfirmationForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label="パスワード"
    )