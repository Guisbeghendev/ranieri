# core/context_processors.py

from django.conf import settings

def project_name_processor(request):
    """
    Context processor para adicionar o nome do projeto a todos os templates.
    """
    return {
        'project_name': settings.PROJECT_NAME
    }