# galleries/views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.models import Galeria, Image, AudienceGroup
from datetime import datetime
# Importa Paginator e EmptyPage, PageNotAnInteger para paginação manual
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# View para listar os grupos de audiência aos quais o usuário logado pertence
class ClientGroupListView(LoginRequiredMixin, ListView):
    model = AudienceGroup
    template_name = 'client_group_list.html'
    context_object_name = 'audience_groups'
    paginate_by = 20  # Paginação para grupos

    def get_queryset(self):
        # Retorna APENAS os grupos de audiência aos quais o usuário logado pertence.
        return self.request.user.audience_groups.all().order_by('name')


# View para listar as galerias de um grupo de audiência específico
class ClientGalleryListView(LoginRequiredMixin, ListView):
    model = Galeria
    template_name = 'client_gallery_list.html'
    context_object_name = 'galleries'
    paginate_by = 20  # Paginação para galerias

    def get_queryset(self):
        group_pk = self.kwargs['group_pk']
        audience_group = get_object_or_404(AudienceGroup, pk=group_pk)

        # Garante que o usuário logado pertence ao grupo selecionado
        if not self.request.user.audience_groups.filter(pk=group_pk).exists():
            return Galeria.objects.none()

        # Lista TODAS as galerias associadas ao grupo de audiência,
        # independentemente do seu status 'is_public'.
        queryset = Galeria.objects.filter(audience_groups=audience_group)

        # Lógica de filtragem por data e busca
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        search_query = self.request.GET.get('q')

        self.filtered_start_date = ''
        self.filtered_end_date = ''
        self.search_query = ''

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__gte=start_date)
                self.filtered_start_date = start_date_str
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__lte=end_date)
                self.filtered_end_date = end_date_str
            except ValueError:
                pass

        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
            self.search_query = search_query

        self.audience_group_name = audience_group.name
        self.audience_group_pk = group_pk

        return queryset.order_by('-event_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audience_group_name'] = self.audience_group_name
        context['audience_group_pk'] = self.audience_group_pk
        context['filtered_start_date'] = self.filtered_start_date
        context['filtered_end_date'] = self.filtered_end_date
        context['search_query'] = self.search_query
        return context


# View para exibir os detalhes de uma galeria privada específica
class ClientGalleryDetailView(LoginRequiredMixin, DetailView):
    model = Galeria
    template_name = 'client_gallery_detail.html'
    context_object_name = 'gallery'
    paginate_by = 20  # Define quantas imagens por página

    def get_queryset(self):
        # Lista TODAS as galerias às quais o usuário logado tem acesso via grupo de audiência.
        return Galeria.objects.filter(
            audience_groups__users=self.request.user
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtém todas as imagens da galeria e as ordena
        images = self.object.images.all().order_by('order', 'created_at')

        # Configura a paginação para as imagens
        paginator = Paginator(images, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            images_page = paginator.page(page)
        except PageNotAnInteger:
            # Se a página não for um inteiro, entrega a primeira página.
            images_page = paginator.page(1)
        except EmptyPage:
            # Se a página estiver fora do intervalo (ex: 9999), entrega a última página de resultados.
            images_page = paginator.page(paginator.num_pages)

        context['images_page'] = images_page  # Renomeado para evitar conflito com 'images' original
        context['is_paginated'] = images_page.has_other_pages()  # Verifica se há outras páginas

        # Adiciona o audience_group_pk ao contexto para o botão "Voltar" no template de detalhes
        if self.object.audience_groups.filter(users=self.request.user).exists():
            context['audience_group_pk'] = self.object.audience_groups.filter(users=self.request.user).first().pk
        else:
            context['audience_group_pk'] = None

        return context
