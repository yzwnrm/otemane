from django import forms
from .models import User
from django.contrib.auth.password_validation import validate_password

class RegistForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'username': '名前/ニックネーム',
            'email': 'メールアドレス',
            'password': 'パスワード',    
        }

    def save(self, commit = False):
        user = super().save(commit=False)
        validate_password(self.changed_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user