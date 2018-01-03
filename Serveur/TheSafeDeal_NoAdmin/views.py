from django.shortcuts import render

# Create your views here.

def about(request):
    return render(request, 'about.html', {})

def login(request):
    return render(request, 'login.html', {})

def home(request):
    return render(request, 'home.html', {})