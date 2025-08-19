# coral/urls.py
from django.urls import path
# Importa a nova view, RepertorioListView, junto com as outras
from .views import CoralHomeView, CoralPageView, RepertorioListView

app_name = 'coral' # Define o namespace do aplicativo

urlpatterns = [
    # Nova rota principal para a home do app Coral
    path('', CoralHomeView.as_view(), name='coral_home'),
    # Nova rota para a página da história
    path('historia/', CoralPageView.as_view(), name='coral_page'),
    # --- NOVA ROTA PARA O REPERTÓRIO ---
    # Conecta a URL '/repertorio/' à view RepertorioListView
    path('repertorio/', RepertorioListView.as_view(), name='repertorio_list'),
]
