from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def hot(request):
    return render(request, 'hot.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def profile(request):
    return render(request, 'profile.html')

def question(request):
    return render(request, 'question.html')

def ask(request):
    return render(request, 'ask.html')

def tag(request):
    return render(request, 'tag.html')
