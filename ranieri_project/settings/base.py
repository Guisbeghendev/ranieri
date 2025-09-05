import os
from pathlib import Path

# Configura o diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Essas configurações serão gerenciadas por variáveis de ambiente em ambientes de produção
# e em um arquivo .env no ambiente local.
# O arquivo .env será lido por um pacote como python-dotenv.
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    # Nossos apps
    'core',
    'home',
    'photographer',
    'galleries',
    'galleries_pub',
    'historia',
    'coral',
    'gremio',
    'simcozinha',
    'brindialogando',
    # o 'admin' sera o admin nativo.
    # Bibliotecas externas
    'guardian', # Django Guardian
    'widget_tweaks'
]

# Definição do modelo de usuário customizado
AUTH_USER_MODEL = 'core.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# Configurações para manipuladores de upload (sem ProgressBarUploadHandler)
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

# Aumenta o limite de arquivos por upload (padrão é 1000)
DATA_UPLOAD_MAX_NUMBER_FILES = 5000
FILE_UPLOAD_MAX_MEMORY_SIZE = 2147483648 #2gb


ROOT_URLCONF = 'ranieri_project.urls'

# Configuração do nome do projeto
PROJECT_NAME = 'E.E. PEI Prof. José Ranieri'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.project_name_processor',
                'core.context_processors.css_file_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ranieri_project.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# Static and Media URLs
STATIC_URL = 'static/'
MEDIA_URL = '/media/'


# Redirecionamento após login bem-sucedido
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGIN_URL = 'accounts:login'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django Guardian settings
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
ANONYMOUS_USER_NAME = 'AnonymousUser'
ANONYMOUS_USER_ID = -1

# As configurações abaixo são específicas de ambiente e serão movidas para
# local.py, production.py ou staging.py
# DEBUG = False
# ALLOWED_HOSTS = [...]
# DATABASES = {}
# STATIC_ROOT = ...
# MEDIA_ROOT = ...
# CSRF_COOKIE_SECURE = True
# CELERY_BROKER_URL = ...
# LOGGING = {}