# gremio/urls.py
from django.urls import path
from .views import GremioPageView

app_name = 'gremio' # Define o namespace do aplicativo

urlpatterns = [
    path('', GremioPageView.as_view(), name='gremio_page'),
]

