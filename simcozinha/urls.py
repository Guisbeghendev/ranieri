from django.urls import path
from .views import SimCozinhaPageView

app_name = 'simcozinha'  # Define o namespace do aplicativo

urlpatterns = [
    path('', SimCozinhaPageView.as_view(), name='simcozinha_page'),
]
