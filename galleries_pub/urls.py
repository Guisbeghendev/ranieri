from django.urls import path
from . import views

app_name = 'galleries_pub'

urlpatterns = [
    # Rota para listar todas as galerias públicas
    path('', views.PublicGalleryListView.as_view(), name='public_gallery_list'),
    # Rota para ver os detalhes de uma galeria pública específica
    path('<int:pk>/', views.PublicGalleryDetailView.as_view(), name='public_gallery_detail'),
    # A rota para o like foi removida.
]