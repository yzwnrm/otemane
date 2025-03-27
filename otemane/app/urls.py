from django.urls import path
from .views import (
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView,UserView
)

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user/', UserView.as_view(), name='user'),
    
]
