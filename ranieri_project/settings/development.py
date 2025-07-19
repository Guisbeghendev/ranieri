from .base import * # Importa todas as configurações de base.py
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] # Hosts permitidos em desenvolvimento

# Database para desenvolvimento (seu MySQL local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ranieri_db', # Nome do seu banco de dados MySQL
        'USER': 'root', # Seu usuário MySQL
        'PASSWORD': 'Gsp@root', # Sua senha MySQL
        'HOST': 'localhost', # Ou o IP do seu servidor MySQL ou 127.0.0.1
        'PORT': '3306', # Porta padrão do MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# SECRET_KEY em desenvolvimento pode ser um valor padrão ou lido de um .env local
# Já está configurado em base.py para ler de env, então não precisa repetir aqui
# Se você quiser uma SECRET_KEY diferente para dev, pode sobrescrever:
# SECRET_KEY = 'seu_secret_key_de_desenvolvimento_aqui'

# Configurações de Celery específicas para desenvolvimento (se diferentes de base.py)
# Por exemplo, se você usa um Redis diferente para dev:
# CELERY_BROKER_URL = 'redis://localhost:6379/1'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

