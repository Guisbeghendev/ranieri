# ranieri_project/celery.py

import os
from celery import Celery

# Define a variável de ambiente padrão para as configurações do Django
# Isso garante que o Celery use as configurações do seu projeto Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings')

# Cria uma instância do aplicativo Celery
# O nome 'ranieri_project' é o nome do seu projeto Django.
app = Celery('ranieri_project')

# Carrega as configurações do Celery a partir do objeto de configurações do Django.
# O prefixo 'CELERY_' significa que todas as variáveis de configuração do Celery
# em settings.py devem começar com 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e registra automaticamente as tarefas de todos os aplicativos Django.
# Isso significa que você não precisa adicionar manualmente as tarefas ao Celery.
# Ele procurará por um arquivo 'tasks.py' em cada um dos seus INSTALLED_APPS.
app.autodiscover_tasks()

# Opcional: Tarefa de depuração para verificar se o Celery está funcionando.
# Você pode chamar isso de um shell Django para testar:
# from ranieri_project.celery import app
# app.send_task('ranieri_project.celery.debug_task')
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
