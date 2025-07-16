# brindialogando/urls.py
from django.urls import path
from .views import BrinDialogandoPageView

app_name = 'brindialogando' # Define o namespace do aplicativo

urlpatterns = [
    path('', BrinDialogandoPageView.as_view(), name='brindialogando_page'),
]

