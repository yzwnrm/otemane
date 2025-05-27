from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import(
    TemplateView, CreateView, FormView, View, 
    ListView, UpdateView, DeleteView
)
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from collections import defaultdict
from django.utils import timezone
from django.utils.timezone import now
from calendar import monthrange, Calendar
from operator import itemgetter
from datetime import date, datetime
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .forms import(
    UserLoginForm, CustomPasswordResetForm,
    UserRegistrationForm, UserUpdateForm,  ChildrenForm, ChildUpdateForm,
    HelpsForm, RewardsForm, PasswordConfirmationForm, FamilyUpdateForm
)
from django.core.paginator import Paginator
from django.views import View
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView, 
)
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from .models import Family, Children, Helps, Reactions, Records, HelpLists
from app.models import User, Invitation, Children
from django.contrib.auth.mixins import LoginRequiredMixin
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

        selected_child_id = request.GET.get('child_id')
        if selected_child_id:
            request.session['selected_child_id'] = selected_child_id
        else:
            selected_child_id = request.session.get('selected_child_id') or 'all'

        if selected_child_id == "all":
            selected_child = "all"
        else:
            selected_child = Children.objects.filter(id=selected_child_id, family=family).first()

        monthly_rewards = defaultdict(lambda: {
            "money": 0,
            "sweets": 0,
            "detail": 0,
            "heart": 0,
            "smile": 0,
            "good": 0,
            "flower": 0,
            "nice": 0,
        })
        monthly_records = []
        
        if selected_child == "all":
        
            # 「全員」の場合、各子どもごとに集計
            for child in children:
                
                monthly_rewards[child.child_name] = {
                    "money": 0,
                    "sweets": 0,
                    "detail": 0,
                    "heart": 0,
                    "smile": 0,
                    "good": 0,
                    "flower": 0,
                    "nice": 0,
                }
                monthly_records.append({
                    "child": child.child_name,
                    "records": []
                })

            for child in children:
                rewards_summary = defaultdict(int)
                child_records = []

                helps = child.helps.prefetch_related('rewards', 'records__reactions')
                for help in helps:
                    for record in help.records.all():
                        if not record.achievement_date:
                            continue

                        record_month = record.achievement_date.strftime('%Y-%m')
                        if record_month != month_str:
                            continue 

                        for reward in help.rewards.all():
                            if reward.reward_type == 1:
                                rewards_summary["money"] += reward.reward_prize or 0
                            elif reward.reward_type == 0:
                                rewards_summary["sweets"] += 1
                            elif reward.reward_type == 2:
                                rewards_summary["detail"] += 1

                        for reaction in record.reactions.all():
                            if reaction.reaction_image == 0:
                                rewards_summary["heart"] += 1
                            elif reaction.reaction_image == 1:
                                rewards_summary["smile"] += 1
                            elif reaction.reaction_image == 2:
                                rewards_summary["good"] += 1
                            elif reaction.reaction_image == 3:
                                rewards_summary["flower"] += 1
                            elif reaction.reaction_image == 4:
                                rewards_summary["nice"] += 1

                        child_records.append({
                            "date": record.achievement_date.strftime('%Y-%m-%d'),
                            "help": help.help_name,
                            "reward": [
                                {
                                    "type": r.get_reward_type_display(),
                                    "prize": r.reward_prize,
                                    "detail": r.reward_detail
                                } for r in help.rewards.all()
                            ],
                            "reaction": "".join([r.get_reaction_image_display() for r in record.reactions.all()])
                        })
                monthly_rewards[child.child_name] = dict(rewards_summary)
                
                for record_item in monthly_records:
                    if record_item["child"] == child.child_name:
                        record_item["records"] = sorted(child_records, key=itemgetter('date'))
                        break

            for record_group in monthly_records:
                money = 0
                sweets = 0
                detail = 0
                for record in record_group['records']:
                    for reward in record['reward']:
                        if reward['type'] == 'おかね':
                            money += int(reward['prize']) if reward['prize'] else 0
                        elif reward['type'] == 'おかし':
                            sweets += 1
                        elif reward['type'] == 'おねがい':
                            detail += 1
                record_group['money_total'] = money
                record_group['sweets_total'] = sweets
                record_group['detail_total'] = detail
    
        if selected_child_id and selected_child!= "all":
            
            rewards_summary = defaultdict(int)
            child_records = []
            
            helps = selected_child.helps.prefetch_related(
                'rewards', 
                Prefetch('records', queryset=Records.objects.prefetch_related('reactions'))
            )
 
            for help in helps:
                for record in help.records.all():
                    if not record.achievement_date:
                        continue

                    record_month = record.achievement_date.strftime('%Y-%m')
                    if record_month != month_str:
                        continue 

                    for reward in help.rewards.all():
                        if reward.reward_type == 1:  # おかね
                            monthly_rewards[record_month]["money"] += reward.reward_prize or 0
                        elif reward.reward_type == 0:  # おかし
                            monthly_rewards[record_month]["sweets"] += 1
                        elif reward.reward_type == 2:  # おねがい
                            monthly_rewards[record_month]["detail"] += 1
  
                    for reaction in record.reactions.all():
                        if reaction.reaction_image == 0:
                            monthly_rewards[record_month]["heart"] += 1
                        elif reaction.reaction_image == 1:
                            monthly_rewards[record_month]["smile"] += 1
                        elif reaction.reaction_image == 2:
                            monthly_rewards[record_month]["good"] += 1
                        elif reaction.reaction_image == 3:
                            monthly_rewards[record_month]["flower"] += 1
                        elif reaction.reaction_image == 4:
                            monthly_rewards[record_month]["nice"] += 1
                            
                    child_records.append({
                        "date": record.achievement_date.strftime('%Y-%m-%d'),
                        "help": help.help_name,
                        "reward": [
                            {
                                "type": r.get_reward_type_display(),
                                "prize": r.reward_prize,
                                "detail": r.reward_detail
                            } for r in help.rewards.all()
                        ],
                        "reaction": "".join([r.get_reaction_image_display() for r in record.reactions.all()])
                    })

            monthly_rewards[selected_child.child_name] = dict(rewards_summary)
            monthly_records = [{
                "child": selected_child.child_name,
                "records": sorted(child_records, key=itemgetter('date'))
            }]


        context = {
            'children': children,
            'selected_child': selected_child,
            'monthly_rewards': dict(monthly_rewards),
            'monthly_records': monthly_records,
            'current_month': month_str,
            'selected_child_id': selected_child_id,  
        }

        
        return render(request, 'home.html', context)

        

 
class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'regist.html'
    success_url = reverse_lazy('app:regist_done') 

    def form_valid(self, form):
        user = form.save(commit=False) 
        relationship = form.cleaned_data['relationship']
        
        family = Family.objects.create()
        user.family = family
        user.relationship = relationship
        user.save()

        login(self.request, user)

        return redirect('app:child_regist')

class UserLoginView(FormView):
    template_name = 'user_login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None,"メールアドレスまたはパスワードが正しくありません。")
            return self.form_invalid(form)

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
    success_url = reverse_lazy('app:password_reset_done')  
    form_class = CustomPasswordResetForm

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
            family_id = user.family.id
            return redirect('app:family_info', family_id=family_id) 
        return render(request, self.template_name, {'user_form': user_form})

class FamilyUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'family_update.html' 
    form_class = FamilyUpdateForm
    
   
    def dispatch(self, request, *args, **kwargs):
        self.family_id = request.GET.get("family_id")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if self.family_id:
            return get_object_or_404(User, id=self.family_id)
        return super().get_object(queryset)

    def form_valid(self, form):
        if not form.has_changed():
            # フォームに変更がない場合、保存せずリダイレクト
            messages.info(self.request, "変更されていません。")
            return HttpResponseRedirect(self.get_success_url())  # エラーではないが、再表示
        form.save()
        messages.success(self.request, "家族情報を更新しました。")
        return super().form_valid(form)
    
    def get_queryset(self):
        return User.objects.filter(family=self.request.user.family)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_members = User.objects.filter(family=self.request.user.family)
        selected_user = None
        if self.family_id:
            selected_user = get_object_or_404(User, id=self.family_id)
        context.update({
            'family_members': family_members,
            'selected_user': selected_user,
            'selected_id': self.family_id,
            'family': self.request.user.family,
        })
        return context
    
    def get_success_url(self):
        family_id = self.object.family.id  
        return reverse('app:family_info', kwargs={'family_id': family_id})

    
class ChildUpdateView(LoginRequiredMixin,View):
    template_name = 'child_update.html'

    def get_context_data(self, child):
        family = child.family
        children = Children.objects.filter(family=family)

        context = {
            'child_form': ChildUpdateForm(instance=child),
            'family': family,
            'selected_child': child,
            'children': children,
        }
        return context
    
    def get(self, request, pk):
        child = get_object_or_404(Children, pk=pk)
        context = self.get_context_data(child)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        child = get_object_or_404(Children, pk=pk)
        child_form = ChildUpdateForm(request.POST, instance=child)

        family = child.family

        if child_form.is_valid():
           child_form.save()
           return redirect('app:family_info', family_id=child.family.id)



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
        selected_child_id = self.request.session.get('selected_child_id')
        context['child'] = get_object_or_404(Children, id=child_id)
        context['selected_helps'] = HelpLists.objects.filter(child_id=child_id)  
        context['selected_child_id'] = selected_child_id

        selected_date_str = self.request.GET.get("selected_date")
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()

        context['selected_date'] = selected_date
        context['today_date'] = date.today()


        completed_help_ids = Records.objects.filter(
            child_id=child_id,
            achievement_date=selected_date
        ).values_list('help_id', flat=True)

        uncompleted_helps = HelpLists.objects.filter(child_id=child_id).exclude(help_id__in=completed_help_ids).select_related('help')
        
        context['uncompleted_helps'] = uncompleted_helps
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        
        child_id = self.kwargs['child_id']
        help_ids = request.POST.getlist("help_ids")
        help_id = request.POST.get("help_id") 
        
        if help_id:
        # 単発「できた」
            Records.objects.create(
                child_id=child_id,
                help_id=help_id,
                achievement_date=timezone.now()
            )
        elif help_ids:
        # モーダルで一括「できた」
            for hid in help_ids:
                Records.objects.create(
                    child_id=child_id,
                    help_id=hid,
                    achievement_date=timezone.now()
            )
        else:
        # どちらも指定されていない
            return self.render_to_response({
                **self.get_context_data(),
                'error_message': "おてつだいのIDが指定されていません。"
            })
        
        messages.success(request, '記録ができました。')
        
        return redirect('app:help_lists', child_id=child_id)
    
class BulkRegisterView(View):
    def post(self, request, child_id):
        help_ids = request.POST.getlist('help_ids') 
        selected_date_str = request.POST.get('selected_date')

        if selected_date_str:
            selected_date = parse_date(selected_date_str)
        else:
            selected_date = timezone.now().date()


        if not help_ids:
            return redirect('app:help_lists', child_id=child_id)  

        for help_list_id in help_ids:
            help_list = get_object_or_404(HelpLists, id=help_list_id, child_id=child_id)
            Records.objects.create(
                child=help_list.child,
                help=help_list.help,
                achievement_date=selected_date
            )
        
        messages.success(request, '記録ができました。')
        
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
            child=selected_child,
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

        request.session['selected_child_id'] = str(child_id)

        family = get_object_or_404(Family, user=request.user)
        
        default_helps = Helps.objects.filter(
            is_default=True,
            child__isnull=True
        )

        original_helps = Helps.objects.filter(
            is_default=False,
            child__family=family
        ).exclude(
            help_name__in=default_helps.values_list('help_name', flat=True)
        )

        helps = (default_helps | original_helps).distinct().prefetch_related('rewards').order_by('-created_at')

        paginator = Paginator(helps, 10)  # 1ページ10件
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return self.render_to_response({
            'page_obj': page_obj,
            'child_id': child_id,
            'selected_child_id': request.session.get('selected_child_id'),
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_child_id = self.request.session.get('selected_child_id')
        context['selected_child_id'] = selected_child_id
        return context


    def post(self, request, *args, **kwargs):
        child_id = kwargs['child_id']
        help_id = request.POST.get('help_id')
        current_count = HelpLists.objects.filter(child_id=child_id).count()
        
        if current_count >= 10:
            messages.error(request, "10件までしか選べません")
            return redirect('app:help_chose', child_id=child_id)            
        
        original_help = get_object_or_404(Helps, id=help_id)

        if original_help.is_default:
            if HelpLists.objects.filter(child_id=child_id, help__help_name=original_help.help_name).exists():
                messages.info(request, "すでに選ばれています。")
                return redirect('app:help_chose', child_id=child_id)

            # 複製処理
            new_help = Helps.objects.create(
                help_name=original_help.help_name,
                created_at=now(),
                child_id=child_id,
                is_default=False, 
            )

            # 報酬も複製（1件だけ対象）
            reward = original_help.rewards.first()
            if reward:
                reward.pk = None  
                reward.help = new_help
                reward.save()

            HelpLists.objects.get_or_create(child_id=child_id, help_id=new_help.id)

        else:
            if HelpLists.objects.filter(child_id=child_id, help=original_help).exists():
                messages.info(request, "すでに選ばれています。")
            else:
                HelpLists.objects.create(child_id=child_id, help=original_help)

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
        
        if getattr(help, 'is_default', False):  # is_default が True なら削除させない
            messages.error(request, 'このお手伝いは削除できません。')
        else:
            help.delete()
            messages.success(request, 'お手伝いを1件削除しました。')

    return redirect('app:help_edit_delete')

class SetChildView(View): 
    def post(self, request, *args, **kwargs):

        child_id = request.POST.get('child_id')
        
        if child_id == "all":
            request.session['selected_child_id'] = "all"
        elif child_id:
            family = get_object_or_404(Family, user=request.user)
            child = get_object_or_404(Children, id=child_id, family=family)
            request.session['selected_child_id'] = child.id

        request.session.set_expiry(60 * 60 * 24 * 3)
        
        request.session.modified = True


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

        family = self.request.user.family  # ← あなたのUserモデルに応じて調整
        children_ids = family.children.values_list('id', flat=True)
        
        all_records = Records.objects.filter(
            achievement_date__range=(start_date, end_date),
            child_id__in=children_ids
        )

        record_map = {}
        for r in all_records:
            record_map.setdefault(r.achievement_date, []).append(r)

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
            achievement_date=target_date,
            child__family=request.user.family
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
                "reward": [{
                   "type": r.help.get_reward_type_display(), 
                   "prize": r.help.reward.reward_prize,
                   "detail": r.help.reward.reward_detail,
                }],
                "reaction": reaction.emoji if reaction else "",
            })
    
        context["monthly_records"] = record_data
        
        context["current_month"] = f"{year}-{str(month).zfill(2)}"
        
        monthly_records = json.dumps(monthly_records, cls=DjangoJSONEncoder)
        return context

def portfolio(request):
    return render(request, 'portfolio.html')