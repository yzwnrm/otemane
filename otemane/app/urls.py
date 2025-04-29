from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    UserRegisterView, HomeView, UserLoginView,
    UserLogoutView, UserView, PasswordChangeDone, AccountEditView,
    PasswordChange, RegistDone, GuideView, UserLogoutDone,
    FamilyInfoView, ChildCreateView, InvitePageView, AjaxCreateInviteView, 
    CustomPasswordResetView, ReactionListView, AddReactionAjaxView,
    HelpMakeView, HelpChoseView, HelpListsView, HelpEditDeleteView,
    SetChildView, CalenderView, HelpDeleteView

)
from . import views

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', UserRegisterView.as_view(), name='regist'),
    path('regist_done/', RegistDone.as_view(), name='regist_done'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('logout_done/', UserLogoutDone.as_view(), name='logout_done'),
    path('user/', UserView.as_view(), name='user'),
    path('password_change/', PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', CustomPasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('guide/', GuideView.as_view(), name='guide'),
    path('account/edit/', AccountEditView.as_view(), name='account_edit'),
    path('family_info/<int:family_id>/', FamilyInfoView.as_view(), name='family_info'),
    path('child_regist/', ChildCreateView.as_view(), name='child_regist'),
    path('invite/', InvitePageView.as_view(), name='invite'),
    path('invite/ajax/create/', AjaxCreateInviteView.as_view(), name='ajax_create_invite'),
    path('reactions/', ReactionListView.as_view(), name='reactions'),
    path('add_reaction/', AddReactionAjaxView.as_view(), name='add_reaction'),
    path('help/make/', HelpMakeView.as_view(), name='help_make'),
    path('help/list/<int:child_id>/', HelpListsView.as_view(), name='help_lists'),
    path('help/chose/<int:child_id>/', HelpChoseView.as_view(), name='help_chose'),
    path('help_edit_delete/', HelpEditDeleteView.as_view(), name='help_edit_delete'),
    path('help_update/<int:pk>/', views.help_update, name='help_update'),
    path('help_delete/<int:pk>/', HelpDeleteView.as_view(), name='help_delete'),
    path('set-child/', SetChildView.as_view(), name='set_child'),
    # path('calender/<int:pk>/', CalenderView.as_view(), name='calender'),

]
