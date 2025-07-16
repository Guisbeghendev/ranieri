# coral/urls.py
from django.urls import path
from .views import CoralPageView

app_name = 'coral' # Define o namespace do aplicativo

urlpatterns = [
    path('', CoralPageView.as_view(), name='coral_page'),
]

