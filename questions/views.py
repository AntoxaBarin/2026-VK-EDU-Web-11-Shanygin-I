from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Question, Tag
from .utils import paginate


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request)
    return render(request, 'questions/tag.html', {'page': page, 'tag_name': tag_name})


def question(request, question_id):
    q = get_object_or_404(
        Question.objects
        .select_related('author', 'author__profile')
        .prefetch_related('tags')
        .annotate(answers_count=Count('answers')),
        pk=question_id,
    )
    answers = q.answers.select_related('author', 'author__profile').order_by('-is_correct', '-votes')
    page = paginate(answers, request)
    return render(request, 'questions/question.html', {'question': q, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
