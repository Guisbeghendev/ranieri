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


# --- VIEW DE REPERTÓRIO SIMPLES ---
class RepertorioListView(ListView):
    model = Repertorio_Coral
    template_name = 'repertorio_list.html'
    context_object_name = 'repertorio_list'

    # A ordenação será feita automaticamente pelo 'ordering' do seu modelo
    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
