# historia/urls.py
from django.urls import path
from .views import HistoriaPageView

app_name = 'historia' # Define o namespace do aplicativo

urlpatterns = [
    path('', HistoriaPageView.as_view(), name='historia_page'),
]
