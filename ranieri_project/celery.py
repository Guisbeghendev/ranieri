import os
from celery import Celery

# Verifica se DJANGO_SETTINGS_MODULE já foi definido.
# Se não, define um padrão (geralmente para desenvolvimento).
# Isso é crucial para que o Celery use as configurações corretas
# baseadas no ambiente (desenvolvimento ou produção).
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings.development')

app = Celery('ranieri_project')

# Carrega as configurações do Celery a partir do objeto de configurações do Django.
# O namespace='CELERY' significa que todas as variáveis de configuração do Celery
# em settings.py (ou development.py/production.py) devem começar com 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e registra automaticamente as tarefas de todos os aplicativos Django.
# Ele procurará por um arquivo tasks.py em cada um dos seus INSTALLED_APPS.
app.autodiscover_tasks()

# Opcional: Tarefa de depuração para verificar se o Celery está funcionando.
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

