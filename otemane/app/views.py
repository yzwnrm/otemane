from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import(
    TemplateView, CreateView, FormView, View, 
    ListView, DetailView, UpdateView, DeleteView
)
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from collections import defaultdict
from django.utils import timezone
from django.utils.timezone import now, localtime
from calendar import monthrange, Calendar
from datetime import date, datetime
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .forms import(
    UserLoginForm,
    #   RequestPasswordResetForm, SetNewPasswordForm, 
    UserRegistrationForm, UserUpdateForm,  ChildrenForm, ChildUpdateForm,
    HelpsForm, RewardsForm, RewardsFormSet, PasswordConfirmationForm
)
from django.core.paginator import Paginator
from django.views import View
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
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
from collections import defaultdict

import uuid, json, logging
logger = logging.getLogger(__name__)

UserModel = get_user_model()

class HomeView(LoginRequiredMixin, View):
    login_url = 'app:user_login'

    def get(self, request):
        family = request.user.family
        children = family.children.all()
 
        month_str = request.GET.get('month') or now().strftime('%Y-%m') 
        current_month = datetime.strptime(month_str, '%Y-%m')

        selected_child_id = request.GET.get('child_id') or request.session.get('selected_child_id')
        selected_child = None
        if selected_child_id:
            selected_child = Children.objects.filter(id=selected_child_id, family=family).first()
 
        monthly_rewards = defaultdict(lambda: {
            "money": 0,
            "sweets": 0,
            "heart": 0,
            "smile": 0,
            "good": 0,
            "flower": 0,
            "nice": 0,
        })
        monthly_records = []
 
        if selected_child:
            helps = selected_child.helps.prefetch_related('rewards', 'records__reactions')
 
            for help in helps:
                for record in help.records.all():
                    if record.achievement_date:
                        month = record.achievement_date.strftime('%Y-%m')
 
                         # 報酬
                        if month == month_str:
                            for reward in help.rewards.all():
                                if reward.reward_type == 1:  # おかね
                                    monthly_rewards[month]["money"] += reward.reward_prize or 0
                                elif reward.reward_type == 0:  # おかし
                                    monthly_rewards[month]["sweets"] += 1
                        
                        if month == month_str:
                            monthly_records.append({
                                "date": record.achievement_date.strftime('%Y-%m-%d'),
                                "help": help.help_name,
                                "reward": ", ".join([r.get_reward_type_display() for r in help.rewards.all()]),
                                "reaction": "".join([r.get_reaction_image_display() for r in record.reactions.all()])
                            })
                         # リアクション
                        for reaction in record.reactions.all():
                            if reaction.reaction_image == 0:  # 💗
                                monthly_rewards[month]["heart"] += 1
                            elif reaction.reaction_image == 1:  # 😊
                                monthly_rewards[month]["smile"] += 1
                            elif reaction.reaction_image == 2:  # 👍
                                monthly_rewards[month]["good"] += 1
                            elif reaction.reaction_image == 3:  # 🌸
                                monthly_rewards[month]["flower"] += 1
                            elif reaction.reaction_image == 4:  # 😎
                                monthly_rewards[month]["nice"] += 1
        context = {
            'children': children,
            'selected_child': selected_child, 
            'monthly_rewards': dict(monthly_rewards),
            'monthly_records': monthly_records,
            'current_month': month_str,
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

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('mypage_authenticated'):
            return redirect('app:mypage_password')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        children = Children.objects.filter(family__user=self.request.user)
        context['records'] = Records.objects.filter(child__in=children).select_related('help', 'child')
        context['family'] = self.request.user.family
        return context

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
            
            invitation = Invitation.objects.create(
                family=request.user.family,
                invitation_URL=uuid.uuid4().hex,
                status=0
            )
            full_url = request.build_absolute_uri(invitation.get_invite_url())
            return JsonResponse({'url': full_url})
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password/password_reset.html'
    email_template_name = 'password/password_reset_email.txt'
    # subject_template_name = 'registration/password_reset_subject.txt'  # これがないとエラー出るかも
    success_url = reverse_lazy('app:password_reset_done')  

    def get_users(self, email):
        return UserModel.objects.filter(email__iexact=email, is_active=True)
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password/password_reset_confirm.html'
    success_url = reverse_lazy('app:password_reset_complete')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password/password_reset_complete.html'

class FamilyInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'family_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_id = self.kwargs['family_id']
        family = get_object_or_404(Family, id=family_id)

        context['family'] = family
        context['user'] = User.objects.filter(family=family)
        context['child'] = Children.objects.filter(family=family)

        return context
    
class UserUpdateView(LoginRequiredMixin, View):
    model = User
    template_name = 'user_update.html'
    # login_url = 'user_login'

class UserUpdateView(LoginRequiredMixin, View):
    template_name = 'user_update.html'  
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user_form = UserUpdateForm(instance=user)
        return render(request, self.template_name, {'user_form': user_form})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user_form = UserUpdateForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            return redirect('app:family_info') 
        return render(request, self.template_name, {'user_form': user_form})

class ChildUpdateView(LoginRequiredMixin,View):
    model = Children
    template_name = 'child_update.html'

    def get(self, request, pk):
        child = get_object_or_404(Children, pk=pk)
        child_form = ChildUpdateForm(instance=child)
        family = child.family 

        return render(request, self.template_name, {
            'child_form': child_form,
            'family': family,  
        })

    def post(self, request, pk):
        child = get_object_or_404(Children, pk=pk)
        child_form = ChildUpdateForm(request.POST, instance=child)

        family = child.family

        if child_form.is_valid():
            child_form.save()
            return redirect('app:family_info', family_id=family.id)
        return render(request, self.template_name, {
            'child_form': child_form,
            'family': family,
        })

class ChildDeleteView(LoginRequiredMixin, DeleteView):
    model = Children
    template_name = 'child_delete.html'
    success_url = reverse_lazy('app:family_info')

    def get_queryset(self):
        return Children.objects.filter(family=self.request.user.family)

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True})
        return super().delete(request, *args, **kwargs)

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user_delete.html'
    success_url = reverse_lazy('app:family_info')

    def get_queryset(self):
        return User.objects.filter(family=self.request.user.family)

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True})
        return super().delete(request, *args, **kwargs)

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
            'rewards_form': RewardsForm(),
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
            
            help_obj = helps_form.save(commit=False)
            help_obj.child = child 
            help_obj.save()

            reward_obj = rewards_form.save(commit=False)
            reward_obj.help = help_obj  
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
        context['selected_helps'] = HelpLists.objects.filter(child_id=child_id)  
        
        completed_help_ids = Records.objects.filter(child_id=child_id).values_list('help_id', flat=True)
        uncompleted_helps = HelpLists.objects.filter(child_id=child_id).exclude(help_id__in=completed_help_ids).select_related('help')
        context['uncompleted_helps'] = uncompleted_helps

        return context

    def post(self, request, *args, **kwargs):
        child_id = self.kwargs['child_id']
        help_ids = request.POST.getlist("help_ids")
        
        if not help_ids:
            return self.render_to_response({
                **self.get_context_data(),
                'error_message': "おてつだいのIDが指定されていません。"
            })

        child = get_object_or_404(Children, id=child_id)
        # help_item = get_object_or_404(Helps, id=help_id)

        for help_id in help_ids:
            Records.objects.create(
                child_id=child_id,
                help_id=help_id,
                achievement_date=timezone.now()  # 現在の日付を設定
            )
        
        return redirect('app:help_lists', child_id=child_id)
    
class BulkRegisterView(View):
    def post(self, request, child_id):
        selected_ids = request.POST.getlist('selected_helps') 
        if not selected_ids:
            return redirect('app:help_lists', child_id=child_id)  

        for help_list_id in selected_ids:
            help_list = get_object_or_404(HelpLists, id=help_list_id, child_id=child_id)
            Records.objects.create(
                child=help_list.child,
                help=help_list.help,
                achievement_date=timezone.now()
            )

        return redirect('app:help_lists', child_id=child_id)
    
class ReactionListView(LoginRequiredMixin, TemplateView):
    template_name = 'reactions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = self.request.user.family
        children = Children.objects.filter(family=family)
        
        selected_child_id = self.request.GET.get("child_id")
        if selected_child_id:
            selected_child = get_object_or_404(Children, id=selected_child_id, family=family)
        else:
            selected_child = children.first()
           
        records = Records.objects.filter(
            child__in=children,
            reactions__isnull=True
        ).select_related('help', 'child')

        context.update({
            "children": children,
            "selected_child": selected_child,
            "records": records,
            "REACTION_CHOICES": Reactions.REACTION_CHOICES,
        })
        return context
    
@method_decorator(csrf_exempt, name='dispatch')
class AddReactionAjaxView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            record_id = data.get('record_id')
            reaction_image = data.get('reaction_image')

            if not record_id or reaction_image is None:
                return JsonResponse({'success': False, 'error': 'レコードまたはリアクションが指定されていません。'}, status=400)

            record = get_object_or_404(Records, id=record_id)

            reaction, created = Reactions.objects.get_or_create(
                record=record,
                user=request.user,
                defaults={'reaction_image': reaction_image}
            )

            if not created:
                reaction.reaction_image = reaction_image
                reaction.save()

            return JsonResponse({'success': True})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': '無効なJSONです。'}, status=400)
            
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

class HelpEditDeleteView(ListView):   
    model = Helps
    template_name = 'help_edit_delete.html'
    context_object_name = 'helps'

def help_update(request, pk):
    help_instance = Helps.objects.get(pk=pk)
    reward_instance = help_instance.rewards.first()  # 最初の報酬1件を取得

    if request.method == 'POST':
        help_form = HelpsForm(request.POST, instance=help_instance)
        reward_form = RewardsForm(request.POST, instance=reward_instance)

        if help_form.is_valid() and reward_form.is_valid():
            help = help_form.save()
            reward = reward_form.save(commit=False)
            reward.help = help  # 外部キーの再設定（念のため）
            reward.save()
            messages.success(request, 'お手伝いを1件修正しました。')
            return redirect('app:help_edit_delete')
    else:
        help_form = HelpsForm(instance=help_instance)
        reward_form = RewardsForm(instance=reward_instance)

    return render(request, 'help_update.html', {
        'helps_form': help_form,
        'rewards_form': reward_form,
    })

def help_delete(request, pk):
    if request.method == 'POST':
        help = get_object_or_404(Helps, pk=pk)
        help.delete()
        messages.success(request, 'お手伝いを1件削除しました。')
    return redirect('app:help_edit_delete')  

class SetChildView(View):
    def post(self, request, *args, **kwargs):
        child_id = request.POST.get('child_id')
        if child_id:
            family = get_object_or_404(Family, user=request.user)
            child = get_object_or_404(Children, id=child_id, family=family)
            request.session['selected_child_id'] = child.id
        return redirect('app:home')


class CalendarView(TemplateView):
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = int(self.request.GET.get('year', now().year))
        month = int(self.request.GET.get('month', now().month))

        # 該当月の開始・終了日
        start_date = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = date(year, month, end_day)

        # カレンダー情報作成
        cal = Calendar(firstweekday=6)  # 日曜始まり
        month_days = cal.monthdatescalendar(year, month)

        # 該当月の達成記録取得
        all_records = Records.objects.filter(achievement_date__range=(start_date, end_date))
        record_map = {}
        for r in all_records:
            record_map.setdefault(r.achievement_date, []).append(r)

        # テンプレート用構造体に整形
        calendar_weeks = []
        for week in month_days:
            week_days = []
            for day in week:
                week_days.append({
                    'day': day.day,
                    'date': day.isoformat(),
                    'in_month': day.month == month,
                    'records': record_map.get(day, [])
                })
            calendar_weeks.append(week_days)

        context.update({
            'year': year,
            'month': month,
            'calendar_weeks': calendar_weeks,
            'year_range': range(now().year - 5, now().year + 2),
            'month_range': range(1, 13),
        })
        return context



@require_GET
@login_required
def records_by_date(request):
    try:
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': '日付が指定されていません'}, status=400)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': '日付の形式が不正です'}, status=400)

        records = Records.objects.select_related('help', 'child').filter(
            achievement_date=target_date
        )

        data = []
        for record in records:
            data.append({
                'id': record.id,
                'help_name': record.help.help_name,
                'child_name': record.child.child_name,
                'achievement_date': str(record.achievement_date),
            })
        
        return JsonResponse({'records': data})

    except Exception as e:
        print(f"Error in records_by_date view: {e}")
        return JsonResponse({'error': 'サーバーエラーが発生しました'}, status=500)
    
class PasswordConfirmView(LoginRequiredMixin, FormView):  #マイページ用パスワード画面
    template_name = 'mypage_password.html'
    form_class = PasswordConfirmationForm
    success_url = reverse_lazy('app:user')

    def form_valid(self, form):
        password = form.cleaned_data['password']
        user = authenticate(username=self.request.user.email, password=password)
        if user is not None:
            self.request.session['mypage_authenticated'] = True
            return super().form_valid(form)
        else:
            form.add_error(None, 'パスワードが違います')
            return self.form_invalid(form)
        
        
class MonthlyRewardView(TemplateView):
    template_name = 'monthly_rewards.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        month_str = self.request.GET.get('month') or timezone.now().strftime('%Y-%m')
        year, month = map(int, month_str.split('-'))

        child = self.request.user.children.first()

        records = Records.objects.filter(
            child=child,
            date__year=year,
            date__month=month
        ).select_related('help__reward')

        record_data = []
        for r in records:
            reaction = Reactions.objects.filter(record=r).first()
            record_data.append({
                "date": r.date.day,
                "help": r.help.title,
                "reward": r.help.reward.__str__(),
                "reaction": reaction.emoji if reaction else "",
            })

        context["record_data_json"] = record_data
        context["current_month"] = f"{year}-{str(month).zfill(2)}"
        return context
