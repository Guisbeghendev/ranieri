from .base import * # Importa todas as configurações de base.py
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Hosts permitidos em produção
ALLOWED_HOSTS = ['escolajoseranieri.com.br', 'www.escolajoseranieri.com.br', '77.37.68.104']

# Database para produção (lendo de variáveis de ambiente para segurança)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Configurações de segurança adicionais para produção
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True # Redireciona HTTP para HTTPS
SECURE_HSTS_SECONDS = 31536000 # HSTS por 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY' # Protege contra clickjacking

# Configurações de Celery específicas para produção (se diferentes de base.py)
# Por exemplo, se você usa um Redis diferente para prod:
# CELERY_BROKER_URL = config('CELERY_BROKER_URL_PROD', default='redis://seu_redis_prod:6379/0')
# CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND_PROD', default='redis://seu_redis_prod:6379/0')

