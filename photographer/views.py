from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.conf import settings
import json
import os
from datetime import datetime

# Importa a tarefa Celery de processamento de imagem
from photographer.tasks import process_image_task

from core.models import Galeria, Image, User
from .forms import GalleryForm

# Removidas as importações para Django Guardian relacionadas a permissões de objeto,
# pois não serão mais usadas para esse propósito.
# from guardian.mixins import PermissionRequiredMixin as ObjectPermissionRequiredMixin
# from guardian.decorators import permission_required as object_permission_required
from guardian.shortcuts import assign_perm, remove_perm # Manter para atribuição na criação, se necessário


# Mixin para verificar se o usuário é fotógrafo ou admin
# Esta mixin agora será a ÚNICA responsável por verificar as permissões de acesso baseadas no papel (fotógrafo/superuser).
class PhotographerRequiredMixin(LoginRequiredMixin, AccessMixin):
    login_url = reverse_lazy('accounts:login')
    raise_exception = True # Levanta 403 Forbidden se não permitido

    def dispatch(self, request, *args, **kwargs):
        # Primeiro, verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            # Se não autenticado e for AJAX, retorna JSON 403
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Autenticação necessária para realizar esta ação.'}, status=403)
            # Caso contrário, redireciona para o login padrão
            return self.handle_no_permission() # Isso usará self.login_url

        # Verifica se o usuário é um superusuário ou fotógrafo
        # A propriedade is_photographer no modelo User já lida com superusuários
        if not request.user.is_photographer:
            # Se não for superusuário nem fotógrafo
            # Se for AJAX, retorna JSON 403 imediatamente
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Você não tem permissão de fotógrafo para acessar esta área.'}, status=403)
            # Caso contrário, nega a permissão (redireciona ou levanta exceção)
            return self.handle_no_permission() # Isso usará raise_exception=True ou self.login_url

        # Se autenticado e for fotógrafo/superuser, prossegue com o dispatch original
        # Não há mais ObjectPermissionRequiredMixin aqui, pois a lógica é baseada em grupo.
        return super().dispatch(request, *args, **kwargs)

    # Este handle_no_permission é um fallback. O ideal é que o dispatch acima
    # já tenha retornado a resposta JSON para AJAX.
    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Permissão negada para realizar esta ação (fallback AJAX).'}, status=403)
        return super().handle_no_permission()


# --- Views CRUD de Galerias ---

class GalleryListView(PhotographerRequiredMixin, ListView):
    model = Galeria
    template_name = 'gallery_list.html'
    context_object_name = 'galleries'
    paginate_by = 10

    def get_queryset(self):
        queryset = Galeria.objects.all()

        # Filtra por fotógrafo se não for superusuário
        # Apenas galerias criadas pelo fotógrafo logado serão exibidas para ele.
        if not self.request.user.is_superuser:
            queryset = queryset.filter(fotografo=self.request.user)

        # Lógica de filtragem por data
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        self.filtered_start_date = ''
        self.filtered_end_date = ''

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

        # Lógica de filtragem por status público (NOVO)
        is_public_filter = self.request.GET.get('is_public')
        self.filtered_is_public = is_public_filter # Armazena para o contexto

        if is_public_filter:
            if is_public_filter == 'true':
                queryset = queryset.filter(is_public=True)
            elif is_public_filter == 'false':
                queryset = queryset.filter(is_public=False)
            # Se for '', significa "todas" e não aplicamos filtro

        return queryset.order_by('-event_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtered_start_date'] = self.filtered_start_date
        context['filtered_end_date'] = self.filtered_end_date
        context['filtered_is_public'] = self.filtered_is_public # Adiciona ao contexto
        return context


# GalleryDetailView agora usa apenas PhotographerRequiredMixin
# A permissão de visualização é tratada pela lógica de get_queryset ou por permissões globais do grupo.
class GalleryDetailView(PhotographerRequiredMixin, DetailView):
    model = Galeria
    template_name = 'gallery_detail.html'
    context_object_name = 'gallery'
    # permission_required = 'core.view_galeria' # Removido, pois a verificação será via PhotographerRequiredMixin e get_queryset

    def get_queryset(self):
        # Garante que um fotógrafo só possa ver suas próprias galerias
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(fotografo=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all().order_by('order')
        return context


class GalleryCreateView(PhotographerRequiredMixin, CreateView):
    model = Galeria
    form_class = GalleryForm
    template_name = 'gallery_form.html'
    success_url = reverse_lazy('photographer:gallery_list')

    def form_valid(self, form):
        form.instance.fotografo = self.request.user
        response = super().form_valid(form)
        # As permissões do Guardian ainda são importantes para controle de acesso granular por objeto
        # Manter assign_perm aqui se você quiser que o criador da galeria tenha permissões explícitas
        # para a galeria que ele acabou de criar, mesmo que a lógica de acesso seja por grupo.
        # Isso pode ser útil para cenários futuros ou para garantir a propriedade.
        assign_perm('view_galeria', self.request.user, self.object)
        assign_perm('change_galeria', self.request.user, self.object)
        assign_perm('delete_galeria', self.request.user, self.object)
        assign_perm('change_galeria_publicado', self.request.user, self.object)
        messages.success(self.request, "Galeria criada com sucesso!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Criar Nova Galeria'
        return context


# GalleryUpdateView agora usa apenas PhotographerRequiredMixin
class GalleryUpdateView(PhotographerRequiredMixin, UpdateView):
    model = Galeria
    form_class = GalleryForm
    template_name = 'gallery_form.html'
    context_object_name = 'gallery'
    # permission_required = 'core.change_galeria' # Removido

    def get_queryset(self):
        # Garante que um fotógrafo só possa editar suas próprias galerias
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(fotografo=self.request.user)
        return queryset

    def get_success_url(self):
        messages.success(self.request, "Galeria atualizada com sucesso!")
        return reverse_lazy('photographer:gallery_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Galeria: {self.object.name}'
        return context


# GalleryDeleteView agora usa apenas PhotographerRequiredMixin
class GalleryDeleteView(PhotographerRequiredMixin, DeleteView):
    model = Galeria
    template_name = 'gallery_confirm_delete.html'
    context_object_name = 'gallery'
    success_url = reverse_lazy('photographer:gallery_list')
    # permission_required = 'core.delete_galeria' # Removido

    def get_queryset(self):
        # Garante que um fotógrafo só possa deletar suas próprias galerias
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(fotografo=self.request.user)
        return queryset

    def form_valid(self, form):
        messages.success(self.request, "Galeria deletada com sucesso!")
        return super().form_valid(form)


# --- Lógica de Upload de Múltiplas Imagens ---
@method_decorator(require_POST, name='dispatch')
# Removido o decorador object_permission_required, a permissão será verificada pela PhotographerRequiredMixin
class ImageUploadView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        gallery = get_object_or_404(Galeria, pk=pk)

        # Adicionado verificação para garantir que o fotógrafo só pode fazer upload em suas próprias galerias
        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para fazer upload nesta galeria.'}, status=403)

        files = request.FILES.getlist('images')

        if not files:
            return JsonResponse({'status': 'error', 'message': "Nenhuma imagem selecionada para upload."}, status=400)

        uploaded_count = 0
        errors = []

        try:
            with transaction.atomic():
                for i, file in enumerate(files):
                    try:
                        max_order = gallery.images.all().order_by(
                            '-order').first().order if gallery.images.exists() else -1
                        new_order = max_order + 1

                        image_instance = Image.objects.create(
                            galeria=gallery,
                            image_file_original=file,
                            original_file_name=file.name,
                            order=new_order,
                        )
                        uploaded_count += 1
                        process_image_task.delay(image_instance.pk)

                    except Exception as e:
                        errors.append(f"Erro ao salvar/disparar tarefa para imagem {file.name}: {e}")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"Erro crítico durante o upload: {e}"}, status=500)

        if errors:
            return JsonResponse({'status': 'warning',
                                 'message': f"{uploaded_count} imagem(ns) enviada(s) com sucesso, mas houve erros no processamento de algumas: {'; '.join(errors)}"},
                                status=200)
        else:
            return JsonResponse({'status': 'success',
                                 'message': f"{uploaded_count} imagem(ns) enviada(s) com sucesso para a galeria '{gallery.name}'. O processamento está ocorrendo em segundo plano."})


# View para obter o progresso do upload
class UploadProgressView(LoginRequiredMixin, View):
    login_url = reverse_lazy('accounts:login')

    def get(self, request):
        progress_id = None
        if 'X-Progress-ID' in request.GET:
            progress_id = request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in request.META:
            progress_id = request.META['X-Progress-ID']

        if progress_id:
            cache_key = f"upload_progress_{progress_id}"
            if cache_key in request.session:
                progress = request.session[cache_key]
                return JsonResponse(progress)

        return JsonResponse({'percentage': 0, 'uploaded': 0, 'total': 0})


# --- Lógica de Reordenamento de Imagens ---
@method_decorator(require_POST, name='dispatch')
# Removido o decorador object_permission_required
class ImageReorderView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        gallery = get_object_or_404(Galeria, pk=pk)

        # Adicionado verificação para garantir que o fotógrafo só pode reordenar em suas próprias galerias
        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para reordenar imagens nesta galeria.'}, status=403)

        image_ids_order = json.loads(request.body).get('image_ids', [])

        if not isinstance(image_ids_order, list):
            return JsonResponse({'status': 'error', 'message': 'Formato de dados inválido.'}, status=400)

        with transaction.atomic():
            for index, image_id in enumerate(image_ids_order):
                try:
                    image = gallery.images.get(pk=image_id)
                    image.order = index
                    image.save()
                except Image.DoesNotExist:
                    continue
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': f"Erro ao reordenar imagem {image_id}: {e}"},
                                        status=500)

        return JsonResponse({'status': 'success', 'message': 'Imagens reordenadas com sucesso.'})


# --- Lógica de Capa da Galeria ---
@method_decorator(require_POST, name='dispatch')
# Removido o decorador object_permission_required
class SetGalleryCoverView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        gallery = get_object_or_404(Galeria, pk=pk)

        # Adicionado verificação para garantir que o fotógrafo só pode definir capa em suas próprias galerias
        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para definir a capa desta galeria.'}, status=403)

        image_id = json.loads(request.body).get('image_id')

        if not image_id:
            return JsonResponse({'status': 'error', 'message': 'ID da imagem não fornecido.'}, status=400)

        try:
            cover_image = gallery.images.get(pk=image_id)
            gallery.cover_image = cover_image
            gallery.save()

            return JsonResponse({'status': 'success',
                                 'message': f"Imagem '{cover_image.original_file_name}' definida como capa da galeria '{gallery.name}'."})
        except Image.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Imagem não encontrada na galeria.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro interno ao definir capa: {e}'}, status=500)


# NOVO: View para Excluir Imagem Individualmente
@method_decorator(require_POST, name='dispatch')
# Removido o decorador object_permission_required
class ImageDeleteView(PhotographerRequiredMixin, View):
    def post(self, request, gallery_pk, image_pk):
        gallery = get_object_or_404(Galeria, pk=gallery_pk)

        # Adicionado verificação para garantir que o fotógrafo só pode deletar imagens em suas próprias galerias
        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para excluir imagens desta galeria.'}, status=403)

        image_instance = get_object_or_404(Image, pk=image_pk, galeria=gallery)

        try:
            with transaction.atomic():
                # Antes de deletar a instância do banco de dados,
                # deletamos os arquivos físicos associados.
                # Verifica se o arquivo original existe e o deleta
                if image_instance.image_file_original:
                    if os.path.exists(image_instance.image_file_original.path):
                        os.remove(image_instance.image_file_original.path)

                # Verifica se o thumbnail existe e o deleta
                if image_instance.image_file_thumb:
                    if os.path.exists(image_instance.image_file_thumb.path):
                        os.remove(image_instance.image_file_thumb.path)

                # Verifica se a imagem com marca d'água existe e a deleta
                if image_instance.image_file_watermarked:
                    if os.path.exists(image_instance.image_file_watermarked.path):
                        os.remove(image_instance.image_file_watermarked.path)

                # Se a imagem era a capa da galeria, remove a referência
                if gallery.cover_image == image_instance:
                    gallery.cover_image = None
                    gallery.save()

                # Deleta a instância da imagem do banco de dados
                image_instance.delete()

            return JsonResponse({'status': 'success', 'message': 'Imagem excluída com sucesso.'})
        except Exception as e:
            print(f"Erro ao excluir imagem {image_pk}: {e}")
            return JsonResponse({'status': 'error', 'message': f'Erro ao excluir imagem: {e}'}, status=500)
