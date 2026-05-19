import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AnswerForm, QuestionForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag
from .utils import paginate


def _attach_question_votes(page, user):
    if not user.is_authenticated:
        for q in page:
            q.user_vote = 0
        return
    q_ids = [q.pk for q in page]
    vote_map = {
        ql.question_id: ql.value
        for ql in QuestionLike.objects.filter(user=user, question_id__in=q_ids)
    }
    for q in page:
        q.user_vote = vote_map.get(q.pk, 0)


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request)
    _attach_question_votes(page, request.user)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request)
    _attach_question_votes(page, request.user)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request)
    _attach_question_votes(page, request.user)
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

    question_user_vote = 0
    if request.user.is_authenticated:
        ql = QuestionLike.objects.filter(user=request.user, question=q).first()
        if ql:
            question_user_vote = ql.value

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

    if request.user.is_authenticated:
        answer_ids = [a.pk for a in page]
        vote_map = {
            al.answer_id: al.value
            for al in AnswerLike.objects.filter(user=request.user, answer_id__in=answer_ids)
        }
        for answer in page:
            answer.user_vote = vote_map.get(answer.pk, 0)
    else:
        for answer in page:
            answer.user_vote = 0

    return render(request, 'questions/question.html', {
        'question': q,
        'page': page,
        'form': form,
        'question_user_vote': question_user_vote,
    })


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


@login_required
@require_POST
def vote_question(request, question_id):
    try:
        data = json.loads(request.body)
        value = int(data.get('value', 1))
    except (ValueError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)
    if value not in (1, -1):
        return JsonResponse({'error': 'Invalid value'}, status=400)

    with transaction.atomic():
        q_locked = get_object_or_404(Question.objects.select_for_update(), pk=question_id)
        try:
            like = QuestionLike.objects.get(user=request.user, question=q_locked)
            if like.value == value:
                q_locked.votes -= value
                like.delete()
                user_vote = 0
            else:
                q_locked.votes += value - like.value
                like.value = value
                like.save()
                user_vote = value
        except QuestionLike.DoesNotExist:
            QuestionLike.objects.create(user=request.user, question=q_locked, value=value)
            q_locked.votes += value
            user_vote = value
        q_locked.save(update_fields=['votes'])

    return JsonResponse({'votes': q_locked.votes, 'user_vote': user_vote})


@login_required
@require_POST
def vote_answer(request, answer_id):
    try:
        data = json.loads(request.body)
        value = int(data.get('value', 1))
    except (ValueError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)
    if value not in (1, -1):
        return JsonResponse({'error': 'Invalid value'}, status=400)

    with transaction.atomic():
        answer_locked = get_object_or_404(Answer.objects.select_for_update(), pk=answer_id)
        try:
            like = AnswerLike.objects.get(user=request.user, answer=answer_locked)
            if like.value == value:
                answer_locked.votes -= value
                like.delete()
                user_vote = 0
            else:
                answer_locked.votes += value - like.value
                like.value = value
                like.save()
                user_vote = value
        except AnswerLike.DoesNotExist:
            AnswerLike.objects.create(user=request.user, answer=answer_locked, value=value)
            answer_locked.votes += value
            user_vote = value
        answer_locked.save(update_fields=['votes'])

    return JsonResponse({'votes': answer_locked.votes, 'user_vote': user_vote})


@login_required
@require_POST
def mark_correct(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related('question'),
        pk=answer_id,
    )
    if answer.question.author != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    answer.is_correct = not answer.is_correct
    answer.save(update_fields=['is_correct'])
    return JsonResponse({'is_correct': answer.is_correct})
