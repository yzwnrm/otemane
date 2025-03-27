from django.shortcuts import render, redirect
from django.views.generic import(
    TemplateView, CreateView, FormView, View
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegistForm, UserLoginForm
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(TemplateView):
    template_name = 'home.html'
    
class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('app:home')
    
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
        return redirect('app:home')

class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'
