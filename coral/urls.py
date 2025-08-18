# coral/urls.py
from django.urls import path
from .views import CoralHomeView, CoralPageView # Importa ambas as views

app_name = 'coral' # Define o namespace do aplicativo

urlpatterns = [
    # Nova rota principal para a home do app Coral
    path('', CoralHomeView.as_view(), name='coral_home'),
    # Nova rota para a página da história
    path('historia/', CoralPageView.as_view(), name='coral_page'),
]
