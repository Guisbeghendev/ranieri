# accounts/urls.py

from django.urls import path
from . import views # Importe as views do app accounts

app_name = 'accounts' # Define o namespace para o app accounts

urlpatterns = [
    path('register/', views.register_view, name='register'), # Rota para registro
    path('login/', views.login_view, name='login'),      # Rota para login
    path('logout/', views.logout_view, name='logout'),     # Rota para logout
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'), # Rota para o dashboard
    path('profile/', views.ViewProfileView.as_view(), name='profile'), # Rota para exibir sa página de perfil
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'), # Rota para editar o perfil
    path('profile/delete/', views.DeleteAccountView.as_view(), name='delete_account'), # Rota para exclusão da conta
]
