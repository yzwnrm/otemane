from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import(
    TemplateView, CreateView, FormView, View, ListView
)
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from collections import defaultdict
from django.utils.timezone import now
from datetime import datetime
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import(
    UserLoginForm,
    #   RequestPasswordResetForm, SetNewPasswordForm, 
    UserRegistrationForm, UserUpdateForm, 
    ChildrenForm, HelpsForm, RewardsForm
)
from django.core.paginator import Paginator
from django.views import View
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.http import JsonResponse
from .models import Family, Children, Helps, Reactions, Records, Rewards, HelpLists
from app.models import User, Invitation
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import(
    PasswordChangeView, PasswordChangeDoneView, 
)
# from django.contrib.auth.models import 

import uuid

UserModel = get_user_model()

class HomeView(LoginRequiredMixin, View):
    class HomeView(LoginRequiredMixin, View):
        login_url = 'user_login'

    def get(self, request):
        family = get_object_or_404(Family, user=request.user)
        children = Children.objects.filter(family=family)

        # URLのchild_idがあればセッションに保存
        selected_child_id = request.GET.get('child_id')
        if selected_child_id:
            request.session['selected_child_id'] = selected_child_id
        else:
            selected_child_id = request.session.get('selected_child_id')

        selected_child = None
        monthly_rewards = defaultdict(lambda: {"money": 0, "sweets": 0})

        if selected_child_id:
            selected_child = Children.objects.filter(id=selected_child_id, family=family).first()
            if selected_child:
                helps = selected_child.helps.prefetch_related('rewards', 'records')

                for help in helps:
                    for record in help.records.all():
                        if record.achievement_date:
                            month = record.achievement_date.strftime('%Y-%m')
                            for reward in help.rewards.all():
                                if reward.reward_type == 1:  # おかね
                                    monthly_rewards[month]["money"] += reward.reward_prize or 0
                                elif reward.reward_type == 0:  # おかし
                                    monthly_rewards[month]["sweets"] += 1

        context = {
            'children': children,
            'selected_child': selected_child,
            'monthly_rewards': dict(monthly_rewards),
            'current_month': now().strftime('%Y-%m'),
        }

        return render(request, 'home.html', context)
    
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
    # subject_template_name = 'registration/password_reset_subject.txt'  # これがないとエラー出るかも
    success_url = reverse_lazy('app:password_reset_done')  

    def get_users(self, email):
        return UserModel.objects.filter(email__iexact=email, is_active=True)
    
class AddReactionView(View):
    def post(self, request, record_id):
        emoji = request.POST.get('emoji')
        record = Records.objects.get(id=record_id)
        Reactions.objects.create(user=request.user, record=record, reaction_image=emoji)
        return redirect('help_lists', pk=record_id)


class HelpMakeView(FormView):    # おてつだいをつくる
    form_class = HelpsForm
    template_name = 'help_make.html'
    success_url = reverse_lazy('app:help_chose')

    def get_success_url(self):
        selected_child_id = self.request.session.get('selected_child_id')
        return reverse('app:help_chose', kwargs={'child_id': selected_child_id})
    
    def get(self, request):
        return render(request, 'help_make.html', {
            'helps_form': HelpsForm(),
            'rewards_form': RewardsForm()
        })

    def post(self, request):
        helps_form = HelpsForm(request.POST)
        rewards_form = RewardsForm(request.POST)

        # セッションに子どものIDがない場合、エラー処理
        selected_child_id = request.session.get('selected_child_id')
        if not selected_child_id:
            helps_form.add_error(None, "子どもが選択されていません。")
            return render(request, 'help_make.html', {
                'helps_form': helps_form,
                'rewards_form': rewards_form
            })

        # フォームが正しい場合、Help と Reward を保存
        if helps_form.is_valid() and rewards_form.is_valid():
            family = get_object_or_404(Family, user=request.user)
            child = get_object_or_404(Children, id=selected_child_id, family=family)
            
            # help インスタンス作成
            help_obj = helps_form.save(commit=False)
            help_obj.child = child  # 選択した子どもをセット
            help_obj.save()

            # reward インスタンス作成
            reward_obj = rewards_form.save(commit=False)
            reward_obj.help = help_obj  # Help と関連付け
            reward_obj.save()

            return redirect(self.get_success_url())
        
        # フォームが無効な場合
        return render(request, 'help_make.html', {
            'helps_form': helps_form,
            'rewards_form': rewards_form
        })

class HelpListsView(ListView):    #えらんだおてつだい
    template_name = 'help_lists.html'
    context_object_name = 'helps'

    def get_queryset(self):
        child_id = self.kwargs['child_id']
        return HelpLists.objects.filter(child_id=child_id).select_related('help')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs['child_id']
        context['child'] = get_object_or_404(Children, id=child_id)
        return context

    def post(self, request, *args, **kwargs):
        child_id = self.kwargs['child_id']
        help_id = request.POST.get("help_id")

        if 'done' in request.POST:
            help_item = get_object_or_404(HelpLists, child_id=child_id, help_id=help_id)
            # 完了記録を追加（カレンダー等に表示可能）
            Records.objects.create(child_id=child_id, help_id=help_id)
            help_item.delete()
            messages.success(request, "おてつだいを記録しました")
        return redirect('app:help_list', child_id=child_id)
    
class HelpChoseView(TemplateView):   #おてつだいをえらぶ
    template_name = 'help_chose.html'

    def get(self, request, child_id):
        family = get_object_or_404(Family, user=request.user)
        helps = Helps.objects.filter(child__family=family).prefetch_related('rewards').order_by('-created_at')[:30]  # 最大30件
        paginator = Paginator(helps, 10)  # 1ページ10件

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return self.render_to_response({
            'page_obj': page_obj,
            'child_id': child_id,
        })

    def post(self, request, child_id):
        help_id = request.POST.get('help_id')
        current_count = HelpLists.objects.filter(child_id=child_id).count()

        if current_count >= 10:
            messages.error(request, "10件までしか選べません")
        else:
            HelpLists.objects.get_or_create(child_id=child_id, help_id=help_id)

        return redirect('app:help_chose', child_id=child_id)

class HelpEditDeleteView(TemplateView):    #おてつだいの修正・削除
    template_name = 'help_edit_delete.html'

class SetChildView(View):
    def post(self, request, *args, **kwargs):
        child_id = request.POST.get('child_id')
        if child_id:
            family = get_object_or_404(Family, user=request.user)
            child = get_object_or_404(Children, id=child_id, family=family)
            request.session['selected_child_id'] = child.id
        return redirect('app:home')