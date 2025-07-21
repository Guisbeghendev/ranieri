# core/context_processors.py

from django.conf import settings
from core.models import VisitCounter # Importa o novo modelo VisitCounter

def project_name_processor(request):
    """
    Context processor para adicionar o nome do projeto a todos os templates.
    """
    return {
        'project_name': settings.PROJECT_NAME
    }

def visit_counter_processor(request):
    """
    Context processor para incrementar e adicionar o contador de visitas a todos os templates.
    """
    # Incrementa o contador de visitas a cada requisição
    # Usamos o método de classe increment para garantir segurança de concorrência
    total_visits = VisitCounter.increment()
    return {
        'total_visits': total_visits
    }

