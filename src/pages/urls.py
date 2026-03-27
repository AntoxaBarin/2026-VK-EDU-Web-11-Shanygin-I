from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('hot/', views.hot),
    path('login/', views.login),
    path('signup/', views.signup),
    path('profile/', views.profile),
    path('question/', views.question),
    path('ask/', views.ask),
]
