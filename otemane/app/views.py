from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import(
    TemplateView, CreateView, FormView, View, ListView
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import UserUpdateForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from .forms import(
    # RegistForm, 
    UserLoginForm, RequestPasswordResetForm, SetNewPasswordForm, 
    UserRegistrationForm, UserChangeForm, UserProfileForm, 
)
from .models import PasswordResetToken, UserProfile, Family, Childmember
from app.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import(
    PasswordChangeView, PasswordChangeDoneView, 
)
# from django.contrib.auth.models import User
import uuid

class HomeView(TemplateView):
    template_name = 'home.html'
    
class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'regist.html'
    success_url = reverse_lazy('app:regist_done')  #登録後に登録完了画面へ

    def form_valid(self, form):
        # ここでユーザーを保存
        user = form.save()  # ユーザーを保存
        # 追加情報（続柄）を保存
        relationship = form.cleaned_data['relationship']
        UserProfile.objects.create(user=user, relationship=relationship)
        return super().form_valid(form)
    
class RegistDone(TemplateView):
    template_name = 'regist_done.html'


class UserLoginView(FormView):
    template_name = 'user_login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url
    

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_logout.html')
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('app:logout_done')
    
class UserLogoutDone(TemplateView):
    template_name = 'logout_done.html'

class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'

class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('app:password_change_done')
    template_name = 'password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context["form_name"] = "password_change"
        return context

class PasswordChangeDone(LoginRequiredMixin,PasswordChangeDoneView):
    template_name = 'password_change_done.html'


def password_reset_form(request):
    form = RequestPasswordResetForm(request.POST or None)
    message = ''
    if form.is_valid():
        email = form.cleaned_data['email']
        user = get_object_or_404(User, email=email)
        password_reset_token, created = PasswordResetToken.objects.get_or_create(user=user)
        if not created:
            password_reset_token.token = uuid.uuid4()
            password_reset_token.used = False
            password_reset_token.save()
        user.is_active = False
        user.save()
        token = password_reset_token.token
        print(f"{request.scheme}://{request.get_host()}/user/reset_password/{token}")
        message = 'パスワードリセットメールをお送りしました'
    return render(request, 'password_reset_form.html', context={
        'reset_form': form, 'message': message,
    })

def reset_password(request, token):
    password_reset_token = get_object_or_404(
        PasswordResetToken,
        token=token,
        used=False,
    )
    form = SetNewPasswordForm(request.POST or None)
    message = ''
    if form.is_valid():
        user = password_reset_token.user
        password = form.cleaned_data['password1']
        validate_password(password)
        # パスワード更新
        user.set_password(password)
        user.is_active = True
        user.save()

        password_reset_token.used = True
        password_reset_token.save()
        message = 'パスワードをリセットしました。'

    return render(request,'app/password_reset_confirm.html', context={
        'form': form, 'message': message,
        })
    
class GuideView(LoginRequiredMixin, TemplateView):
    template_name = 'guide.html'

@login_required
def account_edit_view(request):
    user = request.user
    profile = user.userprofile  # OneToOne なのでOK

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('app:user')  # 編集後の遷移先
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'user_change.html', context)

class FamilyInfoView(LoginRequiredMixin, ListView):
    model = Childmember
    template_name = 'family_info.html'
    context_object_name = 'children'

    def get_queryset(self):
        family_id = self.kwargs['family_id']
        self.family = get_object_or_404(Family, id=family_id)
        return self.family.children.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_user'] = self.request.user
        context['family'] = self.family
        return context