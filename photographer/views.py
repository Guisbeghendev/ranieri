from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden, Http404  # Importe Http404
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.conf import settings
import json
import os
from datetime import datetime
import unicodedata
import re

# Importa a tarefa Celery de processamento de imagem
from photographer.tasks import process_image_task

from core.models import Galeria, Image, User, AudienceGroup
from .forms import GalleryForm  # GARANTA QUE ESTA LINHA ESTEJA PRESENTE E CORRETA


# Mixin para verificar se o usuário é fotógrafo ou admin
class PhotographerRequiredMixin(LoginRequiredMixin, AccessMixin):
    login_url = reverse_lazy('accounts:login')
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Autenticação necessária para realizar esta ação.'},
                                    status=403)
            return self.handle_no_permission()

        if not request.user.is_photographer and not request.user.is_superuser:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(
                    {'status': 'error', 'message': 'Você não tem permissão de fotógrafo para acessar esta área.'},
                    status=403)
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'status': 'error', 'message': 'Permissão negada para realizar esta ação (fallback AJAX).'}, status=403)
        return super().handle_no_permission()


# --- Views CRUD de Galerias ---

class GalleryListView(ListView):
    model = Galeria
    template_name = 'gallery_list.html'
    context_object_name = 'galleries'
    paginate_by = 10

    def get_queryset(self):
        # Usamos um conjunto para armazenar PKS únicos de galerias visíveis
        visible_gallery_pks = set()

        # 1. Superusuários veem todas as galerias
        if self.request.user.is_superuser:
            visible_gallery_pks.update(Galeria.objects.values_list('pk', flat=True))
        else:
            # 2. Todos os usuários autenticados podem ver galerias públicas
            visible_gallery_pks.update(Galeria.objects.filter(is_public=True).values_list('pk', flat=True))

            # 3. Fotógrafos veem suas próprias galerias
            if self.request.user.is_photographer:
                visible_gallery_pks.update(
                    Galeria.objects.filter(fotografo=self.request.user).values_list('pk', flat=True))

            # 4. Usuários veem galerias baseadas em seus grupos de audiência
            user_auth_group_names = self.request.user.groups.values_list('name', flat=True)
            if user_auth_group_names:
                matching_audience_groups = AudienceGroup.objects.filter(name__in=user_auth_group_names)
                # Adiciona os PKS das galerias associadas a esses AudienceGroups
                visible_gallery_pks.update(
                    Galeria.objects.filter(audience_groups__in=matching_audience_groups).values_list('pk', flat=True))

        # Constrói o queryset final a partir dos PKS únicos
        queryset = Galeria.objects.filter(pk__in=list(visible_gallery_pks))

        # Lógica de filtragem por data (aplicada ao queryset já filtrado por permissão)
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

        # Lógica de filtragem por status público
        is_public_filter = self.request.GET.get('is_public')
        self.filtered_is_public = is_public_filter

        if is_public_filter:
            if is_public_filter == 'true':
                queryset = queryset.filter(is_public=True)
            elif is_public_filter == 'false':
                queryset = queryset.filter(is_public=False)

        return queryset.order_by('-event_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # LINHA CORRIGIDA AQUI
        context['filtered_start_date'] = self.filtered_start_date
        context['filtered_end_date'] = self.filtered_end_date
        context['filtered_is_public'] = self.filtered_is_public
        return context


class GalleryDetailView(DetailView):
    model = Galeria
    template_name = 'gallery_detail.html'
    context_object_name = 'gallery'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        gallery = get_object_or_404(queryset, pk=self.kwargs['pk'])

        can_view = False

        if self.request.user.is_photographer and gallery.fotografo == self.request.user:
            can_view = True
        elif gallery.is_public:
            can_view = True
        else:
            user_auth_group_names = self.request.user.groups.values_list('name', flat=True)
            if gallery.audience_groups.filter(name__in=user_auth_group_names).exists():
                can_view = True

        if not can_view:
            raise Http404("A galeria não foi encontrada ou você não tem permissão para visualizá-la.")

        return queryset.filter(pk=self.kwargs['pk'])

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


class GalleryUpdateView(PhotographerRequiredMixin, UpdateView):
    model = Galeria
    form_class = GalleryForm
    template_name = 'gallery_form.html'
    context_object_name = 'gallery'

    def get_queryset(self):
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


class GalleryDeleteView(PhotographerRequiredMixin, DeleteView):
    model = Galeria
    template_name = 'gallery_confirm_delete.html'
    context_object_name = 'gallery'
    success_url = reverse_lazy('photographer:gallery_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(fotografo=self.request.user)
        return queryset

    def form_valid(self, form):
        messages.success(self.request, "Galeria deletada com sucesso!")
        return super().form_valid(form)


# --- Lógica de Upload de Múltiplas Imagens ---
@method_decorator(require_POST, name='dispatch')
class ImageUploadView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        gallery = get_object_or_404(Galeria, pk=pk)

        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse(
                {'status': 'error', 'message': 'Você não tem permissão para fazer upload nesta galeria.'}, status=403)

        files = request.FILES.getlist('images')

        if not files:
            return JsonResponse({'status': 'error', 'message': "Nenhuma imagem selecionada para upload."}, status=400)

        uploaded_count = 0
        errors = []

        for i, file in enumerate(files):
            try:
                with transaction.atomic():
                    max_order = gallery.images.all().order_by(
                        '-order').first().order if gallery.images.exists() else -1
                    new_order = max_order + 1

                    sanitized_file_name = unicodedata.normalize('NFKD', file.name).encode('ascii', 'ignore').decode(
                        'ascii')
                    sanitized_file_name = re.sub(r'[^\w\s.-]', '', sanitized_file_name).strip()
                    sanitized_file_name = re.sub(r'\s+', '_', sanitized_file_name)

                    image_instance = Image.objects.create(
                        galeria=gallery,
                        image_file_original=file,
                        original_file_name=sanitized_file_name,
                        order=new_order,
                    )
                    uploaded_count += 1
                    process_image_task.delay(image_instance.pk)

            except Exception as e:
                errors.append(f"Erro ao salvar/disparar tarefa para imagem {file.name}: {e}")

        if errors:
            return JsonResponse({'status': 'warning',
                                 'message': f"{uploaded_count} imagem(ns) enviada(s) com sucesso, mas houve erros no processamento de algumas: {'; '.join(errors)}"},
                                status=200)
        else:
            return JsonResponse({'status': 'success',
                                 'message': f"{uploaded_count} imagem(ns) enviada(s) com sucesso para a galeria '{gallery.name}'. O processamento está ocorrendo em segundo plano."})


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
class ImageReorderView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        gallery = get_object_or_404(Galeria, pk=pk)

        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse(
                {'status': 'error', 'message': 'Você não tem permissão para reordenar imagens nesta galeria.'},
                status=403)

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
class SetGalleryCoverView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        gallery = get_object_or_404(Galeria, pk=pk)

        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse(
                {'status': 'error', 'message': 'Você não tem permissão para definir a capa desta galeria.'}, status=403)

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
class ImageDeleteView(PhotographerRequiredMixin, View):
    def post(self, request, gallery_pk, image_pk):
        gallery = get_object_or_404(Galeria, pk=gallery_pk)

        if not request.user.is_superuser and gallery.fotografo != request.user:
            return JsonResponse(
                {'status': 'error', 'message': 'Você não tem permissão para excluir imagens desta galeria.'},
                status=403)

        image_instance = get_object_or_404(Image, pk=image_pk, galeria=gallery)

        try:
            with transaction.atomic():
                if image_instance.image_file_original:
                    if os.path.exists(image_instance.image_file_original.path):
                        os.remove(image_instance.image_file_original.path)

                if image_instance.image_file_thumb:
                    if os.path.exists(image_instance.image_file_thumb.path):
                        os.remove(image_instance.image_file_thumb.path)

                if image_instance.image_file_watermarked:
                    if os.path.exists(image_instance.image_file_watermarked.path):
                        os.remove(image_instance.image_file_watermarked.path)

                if gallery.cover_image == image_instance:
                    gallery.cover_image = None
                    gallery.save()

                image_instance.delete()

            return JsonResponse({'status': 'success', 'message': 'Imagem excluída com sucesso.'})
        except Exception as e:
            print(f"Erro ao excluir imagem {image_pk}: {e}")
            return JsonResponse({'status': 'error', 'message': f'Erro ao excluir imagem: {e}'}, status=500)
