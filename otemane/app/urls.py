from django.urls import path
from .views import (HomeView)

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
]
