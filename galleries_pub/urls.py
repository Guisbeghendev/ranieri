# galleries_pub/urls.py
from django.urls import path
from . import views

app_name = 'galleries_pub' # Define o namespace da URL para este app

urlpatterns = [
    # Rota para listar todas as galerias públicas
    path('', views.PublicGalleryListView.as_view(), name='public_gallery_list'),
    # Rota para ver os detalhes de uma galeria pública específica
    path('<int:pk>/', views.PublicGalleryDetailView.as_view(), name='public_gallery_detail'),
    # NOVO: Rota para curtir/descurtir uma galeria pública (via AJAX)
    path('<int:pk>/like/', views.like_public_gallery, name='like_public_gallery'),
]