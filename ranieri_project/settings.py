import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY') # Lendo do ambiente para produção

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False # MUITO IMPORTANTE: DEBUG deve ser False em produção

ALLOWED_HOSTS = ['escolajoseranieri.com.br', 'www.escolajoseranieri.com.br', '77.37.68.104']

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
    # Outras bibliotecas para Celery, etc. serão adicionadas conforme configurarmos
]

# Definição do modelo de usuário customizado
AUTH_USER_MODEL = 'core.User'

# Configuração para Django Guardian (essencial para permissões de objeto)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # Default Django Auth
    'guardian.backends.ObjectPermissionBackend',  # Django Guardian
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # default
    'guardian.backends.ObjectPermissionBackend',
)


# Configurações para manipuladores de upload (sem ProgressBarUploadHandler)
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

# Aumenta o limite de arquivos por upload (padrão é 1000)
DATA_UPLOAD_MAX_NUMBER_FILES = 5000 # Aumentado para suportar mais de 500 imagens
FILE_UPLOAD_MAX_MEMORY_SIZE = 2147483648 #2gb


ROOT_URLCONF = 'ranieri_project.urls'

# config nome do projeto
PROJECT_NAME = 'E.E. PEI Prof. José Ranieri'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # ADICIONE ESTA LINHA para que o Django procure templates na pasta raiz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.project_name_processor',
                'core.context_processors.visit_counter_processor', # NOVO: Contador de visitas
            ],
        },
    },
]

WSGI_APPLICATION = 'ranieri_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'), # Lendo do ambiente
        'USER': config('DB_USER'), # Lendo do ambiente
        'PASSWORD': config('DB_PASSWORD'), # Lendo do ambiente
        'HOST': config('DB_HOST', default='localhost'), # Lendo do ambiente
        'PORT': config('DB_PORT', default='3306'), # Lendo do ambiente
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br' # Altere de 'en-us' para 'pt-br'

TIME_ZONE = 'America/Sao_Paulo' # Altere de 'UTC' para o fuso horário de São Paulo

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/topics/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Onde seus arquivos estáticos de desenvolvimento estarão
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Onde o Django coletará os arquivos para produção

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles' # Onde os uploads (galerias, avatares) serão salvos



# Redirecionamento após login bem-sucedido
LOGIN_REDIRECT_URL = 'accounts:dashboard'
# URL para a página de login (usada por @login_required, etc.)
LOGIN_URL = 'accounts:login'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django Guardian settings
ANONYMOUS_USER_NAME = 'AnonymousUser'
ANONYMOUS_USER_ID = -1  # ou qualquer ID que não conflite com IDs de usuários reais


# Configurações do Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL') # Lendo do ambiente
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND') # Lendo do ambiente
CELERY_ACCEPT_CONTENT = ['json'] # Conteúdo aceito para tarefas
CELERY_TASK_SERIALIZER = 'json' # Serializador para tarefas
CELERY_RESULT_SERIALIZER = 'json' # Serializador para resultados
CELERY_TIMEZONE = 'America/Sao_Paulo' # Use o mesmo fuso horário do Django
CELERY_TASK_TRACK_STARTED = True # Rastreia o estado 'STARTED' da tarefa
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True # Tenta reconectar ao broker na inicialização

# Configurações de segurança adicionais para produção (já estavam aqui)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
