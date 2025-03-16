from django.shortcuts import render
from django.views import View

class HomeView(View):
    def get(self, request):
        return render(request,
                      'home.html')
    
class RegistUserView(View):
    def get(self, request):
        return render(request,
                      'regist.html')
    # Create your views here.