import os
from django.conf import settings


def project_name_processor(request):
    """
    Processador de contexto para adicionar o nome do projeto a todos os templates.
    """
    return {
        'project_name': settings.PROJECT_NAME
    }


def css_file_processor(request):
    """
    Processador de contexto para ler o nome do arquivo CSS mais recente
    e adicioná-lo a todos os templates.
    """
    css_file_name = 'style.css'  # Nome padrão, caso o arquivo de build não seja encontrado.
    build_file_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'last_build.txt')

    # Verifica se o arquivo de build existe e lê o nome do arquivo CSS mais recente.
    if os.path.exists(build_file_path):
        with open(build_file_path, 'r') as f:
            css_file_name = f.read().strip()

    return {
        'css_file': css_file_name
    }
