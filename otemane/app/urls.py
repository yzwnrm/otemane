from django.urls import path
from .views import (
    UserRegisterView, HomeView, UserLoginView,
    UserLogoutView, UserView, PasswordChangeDone, 
    PasswordChange, RegistDone,
)
from . import views

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', UserRegisterView.as_view(), name='regist'),
    path('regist_done/', RegistDone.as_view(), name='regist_done'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user/', UserView.as_view(), name='user'),
    path('password_change/', PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset_form/', views.password_reset_form, name='password_reset_form'),
    path('reset_password<uuid:token>/', views.reset_password, name='reset_password'),

]
