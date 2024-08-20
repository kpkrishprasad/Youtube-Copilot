from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_summary/', views.get_summary, name='get_summary'),
]