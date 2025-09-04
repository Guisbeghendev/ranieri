import os
from pathlib import Path
from ranieri_project.settings.base import *

# --- Configurações Específicas para Staging ---

SECRET_KEY = os.environ.get('SECRET_KEY', 'sua_chave_de_desenvolvimento_aqui')

DEBUG = True

ALLOWED_HOSTS = ['staging.escolajoseranieri.com.br', 'localhost', '127.0.0.1']

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

MEDIA_ROOT = BASE_DIR / 'mediafiles'
MEDIA_URL = '/mediafiles/'

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = 'static/'
