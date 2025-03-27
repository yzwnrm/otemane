from django.urls import path
from .views import (
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView, UserView, 
    # HelpSelectView, CalendarView, HelpMakeView
)

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user/', UserView.as_view(), name='user'),
    # path('help_select/', HelpSelectView.as_view(), name='help_select'),
    # path('calendar/', CalendarView.as_view(), name='calendarr'),
    # path('help_make/', HelpMakeView.as_view(), name='help_make'),
]
