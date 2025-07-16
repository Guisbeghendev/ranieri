# coral/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
import json  # Para passar a lista de nomes de arquivos JSON


class CoralPageView(TemplateView):
    # Caminho do template: coral/templates/coral_page.html
    template_name = 'coral_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista dos nomes dos arquivos JSON dos capítulos, na ordem desejada.
        # Por favor, certifique-se de que esses nomes correspondem aos arquivos que você criou
        # em coral/static/coral/chapters/
        chapter_filenames = [
            'Capitulo1.json',
            'Capitulo2.json',
            # ... adicione mais conforme você criar os arquivos JSON
        ]

        # Passa a lista de nomes de arquivos como uma string JSON para o template.
        context['chapter_filenames_json'] = json.dumps(chapter_filenames)

        return context

