# photographer/urls.py
from django.urls import path
from . import views

app_name = 'photographer'  # Define o namespace da URL para este app

urlpatterns = [
    # URLs para Galerias
    path('galleries/', views.GalleryListView.as_view(), name='gallery_list'),
    path('galleries/new/', views.GalleryCreateView.as_view(), name='gallery_create'),
    path('galleries/<int:pk>/', views.GalleryDetailView.as_view(), name='gallery_detail'),
    path('galleries/<int:pk>/edit/', views.GalleryUpdateView.as_view(), name='gallery_edit'),
    path('galleries/<int:pk>/delete/', views.GalleryDeleteView.as_view(), name='gallery_delete'),

    # URLs para Imagens (ações dentro de uma galeria específica)
    path('galleries/<int:pk>/upload/', views.ImageUploadView.as_view(), name='image_upload'),
    path('galleries/<int:pk>/reorder/', views.ImageReorderView.as_view(), name='image_reorder'),
    path('galleries/<int:pk>/set_cover/', views.SetGalleryCoverView.as_view(), name='set_gallery_cover'),

    # URL para o progresso do upload
    path('upload_progress/', views.UploadProgressView.as_view(), name='upload_progress'),

    # NOVO: URL para deletar imagem individualmente
    # A URL precisa do PK da galeria e do PK da imagem
    path('galleries/<int:gallery_pk>/images/<int:image_pk>/delete/', views.ImageDeleteView.as_view(),
         name='image_delete'),
]
