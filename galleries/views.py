import os
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.models import Galeria, Image, AudienceGroup, GaleriaLike # Importa GaleriaLike
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse # Importa JsonResponse para respostas AJAX
from django.views.decorators.http import require_POST # Para garantir que a view só aceite POST
from django.contrib.auth.decorators import login_required # Para proteger a view de curtidas
from django.template.loader import render_to_string # Para renderizar partes do template


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

        # --- Lógica de Curtidas ---
        # Verifica se o usuário logado já curtiu esta galeria
        user_has_liked = False
        if self.request.user.is_authenticated:
            user_has_liked = GaleriaLike.objects.filter(
                galeria=self.object,
                user=self.request.user
            ).exists()
        context['user_has_liked'] = user_has_liked

        # Conta o total de curtidas para esta galeria
        gallery_likes_count = self.object.likes.count()
        context['gallery_likes_count'] = gallery_likes_count

        # Obtém os usuários que curtiram (para exibição no modal)
        # Limita a 50 usuários para evitar sobrecarga, você pode ajustar este limite
        likers = self.object.likes.select_related('user').order_by('-created_at')[:50]
        context['gallery_likers'] = [like.user.username for like in likers]
        # Adiciona a contagem total de likers para o modal
        context['total_likers_count'] = self.object.likes.count()

        return context


# NOVO: View para alternar (curtir/descurtir) uma galeria
@require_POST # Garante que esta view só aceita requisições POST
@login_required # Garante que apenas usuários logados podem acessar esta view
def like_gallery(request, pk):
    galeria = get_object_or_404(Galeria, pk=pk)
    user = request.user

    # Verifica se o usuário já curtiu esta galeria
    like_exists = GaleriaLike.objects.filter(galeria=galeria, user=user).exists()

    if like_exists:
        # Se já curtiu, remove a curtida (descurtir)
        GaleriaLike.objects.filter(galeria=galeria, user=user).delete()
        liked = False
    else:
        # Se não curtiu, adiciona a curtida
        GaleriaLike.objects.create(galeria=galeria, user=user)
        liked = True

    # Recalcula a contagem de curtidas
    new_likes_count = galeria.likes.count()

    # Obtém os nomes dos usuários que curtiram para atualizar o modal
    likers = galeria.likes.select_related('user').order_by('-created_at')[:50]
    likers_usernames = [like.user.username for like in likers]
    total_likers_count = galeria.likes.count()

    # Retorna uma resposta JSON com o novo estado
    return JsonResponse({
        'liked': liked,
        'likes_count': new_likes_count,
        'likers': likers_usernames,
        'total_likers_count': total_likers_count
    })

