# coral/views.py
import json
from django.views.generic import TemplateView


# Função auxiliar para manter a lógica de listagem de capítulos separada da view
def get_chapter_filenames():
    """
    Retorna a lista de nomes de arquivos JSON dos capítulos na ordem desejada.
    """
    return [
        'Capitulo1.json',
        'Capitulo2.json',
        # ... adicione mais conforme você criar os arquivos JSON
    ]


# Nova view para a página principal do app Coral
class CoralHomeView(TemplateView):
    # Simplesmente renderiza o novo template HTML
    template_name = 'coral/coral_home.html'


# View da página da História do Coral (a view original)
class CoralPageView(TemplateView):
    template_name = 'coral/coral_page.html'  # Ajuste no caminho do template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtém os nomes dos arquivos JSON dos capítulos usando a função auxiliar
        chapter_filenames = get_chapter_filenames()

        # Passa a lista de nomes de arquivos para o template como JSON
        context['chapter_filenames_json'] = json.dumps(chapter_filenames)

        return context
