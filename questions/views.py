from django.shortcuts import render


def index(request):
    return render(request, "questions/index.html")


def hot(request):
    return render(request, "questions/hot.html")


def question(request):
    return render(request, "questions/question.html")


def ask(request):
    return render(request, "questions/ask.html")


def tag(request):
    return render(request, "questions/tag.html")
