from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_summary/', views.get_summary, name='get_summary'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('youtube_research/', views.youtube_research, name='youtube_research'),
    path('email_summary/', views.email_summary, name='email_summary'),
    path('email_research/', views.email_research, name='email_research'),
]
