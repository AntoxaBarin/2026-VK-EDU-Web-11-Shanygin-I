from django.shortcuts import render
from .utils import paginate


def get_stub_questions():
    questions = []
    for i in range(1, 30):
        questions.append(
            {
                "id": i,
                "title": "Question title " + str(i),
                "text": "Question text " + str(i),
                "author": "Sponge Bob",
                "votes": i * 3,
                "answers": i,
                "tags": ["python", "django"],
                "created_at": "2 hours ago",
            }
        )
    return questions


def index(request):
    questions = get_stub_questions()
    page = paginate(questions, request)
    return render(request, "questions/index.html", {"page": page})


def hot(request):
    questions = get_stub_questions()
    # Имитируем сортировку по популярности — переворачиваем список
    page = paginate(questions[::-1], request)
    return render(request, "questions/hot.html", {"page": page})


def tag(request, tag_name):
    questions = get_stub_questions()
    page = paginate(questions, request)
    return render(
        request,
        "questions/tag.html",
        {
            "page": page,
            "tag_name": tag_name,
        },
    )


def question(request, question_id):
    stub_question = {
        "id": question_id,
        "title": "Question title " + str(question_id),
        "text": "Question text " + str(question_id),
        "author": "Sponge Bob",
        "votes": 42,
        "answers_count": 15,
        "tags": ["python", "django"],
        "created_at": "2 hours ago",
    }
    answers = []
    for i in range(1, 16):
        answers.append(
            {
                "id": i,
                "text": "Answer text " + str(i),
                "author": "Patrick",
                "votes": i * 2,
                "is_correct": i == 1,
                "created_at": str(i) + " hours ago",
            }
        )
    page = paginate(answers, request)
    return render(
        request,
        "questions/question.html",
        {
            "question": stub_question,
            "page": page,
        },
    )


def ask(request):
    return render(request, "questions/ask.html")
