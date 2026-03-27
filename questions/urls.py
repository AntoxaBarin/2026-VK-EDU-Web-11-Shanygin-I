from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("question/", views.question, name="question"),
    path("ask/", views.ask, name="ask"),
    path("tag/", views.tag, name="tag"),
]
