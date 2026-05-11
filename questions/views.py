from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, QuestionForm
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

    form = AnswerForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = q
            answer.author = request.user
            answer.save()
            all_answer_pks = list(
                q.answers.order_by('-is_correct', '-votes').values_list('pk', flat=True)
            )
            pos = all_answer_pks.index(answer.pk)
            page_num = pos // 10 + 1
            return redirect(f"{q.get_absolute_url()}?page={page_num}#answer-{answer.pk}")

    return render(request, 'questions/question.html', {'question': q, 'page': page, 'form': form})


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(author=request.user)
            return redirect('question', question_id=q.pk)
    else:
        form = QuestionForm()
    return render(request, 'questions/ask.html', {'form': form})
