from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

class HomeView(View):
    def get(self, request):
        return HttpResponse('<h1>welcome</h1>')

# Create your views here.