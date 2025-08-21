import json
from django.views.generic import TemplateView, ListView
from core.models import Repertorio_Coral


def get_chapter_filenames():
    """
    Retorna a lista de nomes de arquivos JSON dos capítulos na ordem desejada.
    """
    return [
        'Capitulo1.json',
        'Capitulo2.json',
    ]


class CoralHomeView(TemplateView):
    template_name = 'coral_home.html'


class CoralPageView(TemplateView):
    template_name = 'coral_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter_filenames = get_chapter_filenames()
        context['chapter_filenames_json'] = json.dumps(chapter_filenames)
        return context


# --- VIEW DE REPERTÓRIO COM FILTRO POR ANO ---
class RepertorioListView(ListView):
    model = Repertorio_Coral
    template_name = 'repertorio_list.html'
    context_object_name = 'repertorio_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Obtém o ano da URL, se existir (ex: ?ano=2024)
        ano = self.request.GET.get('ano')
        if ano:
            try:
                # Filtra o queryset pelo ano, se o valor for um número válido
                queryset = queryset.filter(inclusion_year=int(ano))
            except (ValueError, TypeError):
                # Ignora o filtro se o valor do ano não for um número
                pass
        # A ordenação por título agora será padrão no modelo, sem causar erro.
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtém a lista de anos únicos para o filtro e a ordena corretamente
        anos_disponiveis = sorted(list(Repertorio_Coral.objects.values_list('inclusion_year', flat=True).distinct()), reverse=True)
        context['anos_disponiveis'] = anos_disponiveis
        context['selected_year'] = self.request.GET.get('ano', '')
        return context
