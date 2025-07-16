# galleries_pub/views.py
from django.views.generic import ListView, DetailView
from core.models import Galeria, Image
from datetime import datetime
from django.db.models import Q


# View para listar todas as galerias públicas
class PublicGalleryListView(ListView):
    model = Galeria
    template_name = 'public_gallery_list.html'
    context_object_name = 'public_galleries'
    paginate_by = 20  # ALTERADO: Número de galerias por página agora é 20

    def get_queryset(self):
        queryset = Galeria.objects.filter(is_public=True)

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__gte=start_date)
                self.filtered_start_date = start_date_str
            except ValueError:
                print(f"Data inicial inválida recebida: {start_date_str}")
                self.filtered_start_date = ''
        else:
            self.filtered_start_date = ''

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__lte=end_date)
                self.filtered_end_date = end_date_str
            except ValueError:
                print(f"Data final inválida recebida: {end_date_str}")
                self.filtered_end_date = ''
        else:
            self.filtered_end_date = ''

        return queryset.order_by('-event_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtered_start_date'] = self.filtered_start_date
        context['filtered_end_date'] = self.filtered_end_date
        return context


# View para exibir os detalhes de uma galeria pública específica
class PublicGalleryDetailView(DetailView):
    model = Galeria
    template_name = 'public_gallery_detail.html'
    context_object_name = 'gallery'

    def get_queryset(self):
        return Galeria.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all().order_by('order', 'created_at')
        return context
