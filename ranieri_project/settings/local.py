import os
from .base import *
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações para Ambiente Local
# DEBUG deve ser True para desenvolvimento
DEBUG = True

# Permite acesso ao host local
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Conexão com Banco de Dados para Ambiente Local (MySQL), usando variáveis do .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Diretórios para arquivos estáticos e de mídia no ambiente local
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Chave secreta, agora importada do arquivo .env
SECRET_KEY = os.environ.get('SECRET_KEY')
