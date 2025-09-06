import os
from pathlib import Path
from ranieri_project.settings.base import *
from dotenv import load_dotenv

load_dotenv()

# --- Configurações Específicas para Staging ---

SECRET_KEY = os.environ.get('SECRET_KEY')

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

# --- Configurações para arquivos estáticos (servidos localmente) ---
STATIC_ROOT = '/var/www/escolajoseranieri.com.br/staging_html/staticfiles/'
STATIC_URL = 'https://staging.escolajoseranieri.com.br/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# --- Configuração do Amazon S3 para arquivos de Mídia ---
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = 'us-east-1'

AWS_STORAGE_BUCKET_NAME = 'ranieristaging'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Define o armazenamento padrão para arquivos de mídia como S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

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
