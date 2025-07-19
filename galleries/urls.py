from django.urls import path
from . import views

app_name = 'galleries'

urlpatterns = [
    # Rota para listar os grupos de audiência do usuário logado (MOD10)
    path('meus-grupos/', views.ClientGroupListView.as_view(), name='client_group_list'),
    # NOVO: Rota para listar as galerias de um grupo de audiência específico (MOD10)
    path('grupo/<int:group_pk>/galerias/', views.ClientGalleryListView.as_view(), name='client_gallery_list'),
    # NOVO: Rota para ver os detalhes de uma galeria privada específica (MOD10)
    path('galeria/<int:pk>/detalhes/', views.ClientGalleryDetailView.as_view(), name='client_gallery_detail'),
    # NOVO: Rota para curtir/descurtir uma galeria (via AJAX)
    path('galeria/<int:pk>/like/', views.like_gallery, name='like_gallery'),
]
