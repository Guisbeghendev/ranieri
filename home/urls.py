# home/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'), # Mapeia a URL raiz para a home_view
]