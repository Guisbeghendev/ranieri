import os
from pathlib import Path
from ranieri_project.settings.base import *

# --- Configurações Específicas para Staging ---

# Adicione esta linha para ler a chave da variável de ambiente do Apache.
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua_chave_de_desenvolvimento_aqui')

DEBUG = True

ALLOWED_HOSTS = ['staging.escolajoseranieri.com.br', 'localhost', '127.0.0.1']

# Configuração do banco de dados para o ambiente de testes (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ranieri_staging_db',
        'USER': 'ranieri_staging_user',
        'PASSWORD': 'Gsp@root2025',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# --- Configurações para arquivos estáticos e de mídia (servidos localmente) ---
# O Django irá coletar todos os arquivos estáticos neste diretório.
# O Apache irá servir este diretório através de um 'Alias'.
STATIC_ROOT = '/var/www/escolajoseranieri.com.br/staging_html/staticfiles/'
STATIC_URL = 'https://staging.escolajoseranieri.com.br/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuração para arquivos de mídia (uploads de usuários)
# Também servidos localmente pelo Apache.
MEDIA_ROOT = '/var/www/escolajoseranieri.com.br/staging_html/mediafiles/'
MEDIA_URL = 'https://staging.escolajoseranieri.com.br/mediafiles/'


# Celery settings para Staging (conforme discutido anteriormente)
CELERY_BROKER_URL = 'amqp://celeryuser:Gsp@ranieri2025@localhost:5672//'
CELERY_RESULT_BACKEND = 'rpc://'

# Nome da fila específica para o ambiente de testes
CELERY_TASK_DEFAULT_QUEUE = 'ranieri_staging_tasks'
CELERY_TASK_QUEUES = {
    'ranieri_staging_tasks': {
        'exchange': 'ranieri_staging_tasks',
        'exchange_type': 'direct',
        'binding_key': 'ranieri_staging_tasks',
    },
}
