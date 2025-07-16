# ranieri_project/__init__.py

# Isso garantirá que o aplicativo Celery seja sempre importado quando o Django iniciar,
# para que as tarefas compartilhadas possam ser usadas.
from .celery import app as celery_app

__all__ = ('celery_app',)
