from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import(
    TemplateView, CreateView, FormView, View, ListView
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import(
    UserLoginForm,
    #   RequestPasswordResetForm, SetNewPasswordForm, 
    UserRegistrationForm, UserUpdateForm, 
    ChildrenForm, HelpsForm, RewardsForm
)

from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model

from django.http import JsonResponse
from .models import Family, Children, Helps, Reactions, Records, Rewards
from app.models import User, Invitation
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import(
    PasswordChangeView, PasswordChangeDoneView, 
)
# from django.contrib.auth.models import User
import uuid

UserModel = get_user_model()

class HomeView(TemplateView):
    template_name = 'home.html'
    
class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'regist.html'
    success_url = reverse_lazy('app:regist_done') 

    def form_valid(self, form):
        user = form.save() 
        relationship = form.cleaned_data['relationship']
        response = super().form_valid(form)
        # 登録後のユーザーにFamilyを紐づけ
        Family.objects.create(user=self.object)
        return response
    
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

class GuideView(LoginRequiredMixin, TemplateView):
    template_name = 'guide.html'

@login_required
def account_edit_view(request):
    user = request.user

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        
        if user_form.is_valid():
            user_form.save()
            return redirect('app:user')  # 編集後の遷移先
    else:
        user_form = UserUpdateForm(instance=user)

    context = {
        'user_form': user_form,
    }
    return render(request, 'user_change.html', context)

class FamilyInfoView(LoginRequiredMixin, ListView):
    model = Children
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
    
class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Children
    form_class = ChildrenForm
    template_name = 'child_regist.html'
    success_url = reverse_lazy('app:home')  

    def form_valid(self, form):
        family = get_object_or_404(Family, user=self.request.user)
        form.instance.family = family 
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class InvitePageView(TemplateView):
    template_name = 'invite.html'

class AjaxCreateInviteView(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            family_id = request.user.family
            invitation = Invitation.objects.create(
                family_id=family_id,
                invitation_URL=uuid.uuid4().hex,
                status=0
            )
            full_url = request.build_absolute_uri(invitation.get_invite_url())
            return JsonResponse({'url': full_url})
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.txt'
    # subject_template_name = 'registration/password_reset_subject.txt'  # これがないとエラー出る場合がある
    success_url = reverse_lazy('app:password_reset_done')  # ハードコーディング避けると安心

    def get_users(self, email):
        return UserModel.objects.filter(email__iexact=email, is_active=True)
    
class AddReactionView(View):
    def post(self, request, record_id):
        emoji = request.POST.get('emoji')
        record = Records.objects.get(id=record_id)
        Reactions.objects.create(user=request.user, record=record, reaction_image=emoji)
        return redirect('help_lists', pk=record_id)


class HelpMakeView(View):    #おてつだいをつくる
    def get(self, request):
        return render(request, 'help_make.html', {
            'helps_form': HelpsForm(),
            'rewards_form': RewardsForm()
        })

    def post(self, request):
        helps_form = HelpsForm(request.POST)
        rewards_form = RewardsForm(request.POST)

        if helps_form.is_valid() and rewards_form.is_valid():
            help_obj = helps_form.save()
            reward_obj = rewards_form.save(commit=False)
            reward_obj.help = help_obj
            reward_obj.save()
            return redirect('app:home')

        return render(request, 'app/help_make.html', {
            'helps_form': helps_form,
            'rewards_form': rewards_form
        })


class HelpChoiceView(TemplateView):    #おてつだいをえらぶ
    template_name = 'help_choice.html'


class HelpChoseView(TemplateView):    #えらんだおてつだい
     template_name = 'help_chose.html'
    
class HelpEditDeleteView(TemplateView):    #おてつだいの修正・削除
    template_name = 'help_edit_delete.html'
