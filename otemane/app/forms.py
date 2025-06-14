from django import forms
from django.forms import modelformset_factory
from app.models import User, Helps
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth import get_user_model
from .models import Children, User, Rewards, RELATIONSHIP_CHOICES

User = get_user_model()

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = ''
        self.fields['email'].widget.attrs.update({
            'placeholder': 'メールアドレスを入力',
            'class': 'form-control center-placeholder'
        })

class UserRegistrationForm(UserCreationForm):
    user_name = forms.CharField(
        label='名前/ニックネーム',
        widget=forms.TextInput(attrs={'class': 'form-control'})
        
    )
    email = forms.EmailField(
        required=True, 
        label='メールアドレス',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    RELATIONSHIP_CHOICES = [
        (0, '母'),
        (1, '父'),
        (2, '祖母'),
        (3, '祖父'),
        (4, '兄'),
        (5, '姉'),
        (6, 'その他'),
    ]
    relationship = forms.ChoiceField(
        choices=RELATIONSHIP_CHOICES, 
        required=True, 
        label='続柄',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='パスワード（再入力）',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['user_name', 'email', 'relationship']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に登録されています。")
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        relationship = getattr(self.instance, 'relationship', None)
        if 'relationship' in self.fields and relationship is not None:
            self.initial['relationship'] = relationship

class UserUpdateForm(forms.ModelForm):
    relationship = forms.ChoiceField(choices=RELATIONSHIP_CHOICES, label='続柄')
    new_email = forms.EmailField(label='新しいメールアドレス', required=False)

    class Meta:
        model = User
        fields = ['user_name', 'relationship', 'email']
        labels = {
            'user_name': '名前/ニックネーム',
            'relationship': '続柄',
            'email': '現在のメールアドレス',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'})  # or 'disabled': 'disabled'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        if new_email and User.objects.exclude(pk=self.instance.pk).filter(email=new_email).exists():
            self.add_error('new_email', 'このメールアドレスは既に使用されています。')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_email = self.cleaned_data.get('new_email')
        if new_email:
            user.email = new_email
        if commit:
            user.save()
        return user

class FamilyUpdateForm(forms.ModelForm):
    relationship = forms.TypedChoiceField(
        choices=RELATIONSHIP_CHOICES,
        coerce=int,
        label='続柄',
        widget=forms.Select()
    )
    class Meta:
        model = User
        fields = ['user_name', 'relationship']
        widgets = {
            'user_name': forms.TextInput(attrs={'placeholder': '変更したい名前/ニックネーム'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        relationship = getattr(self.instance, 'relationship', None)
        if 'relationship' in self.fields and relationship is not None:
            self.initial['relationship'] = relationship 

    
    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
        return user


class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = ['child_name', 'birthday', 'icon']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'icon': forms.RadioSelect
            }
        labels = {
            'child_name': 'なまえ/ニックネーム',
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