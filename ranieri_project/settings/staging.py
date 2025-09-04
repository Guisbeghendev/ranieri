import os
# Importa todas as configurações do seu arquivo settings.py principal
from ranieri_project.settings.base import * # Acessa o arquivo base.py corretamente

# --- Configurações Específicas para Staging ---

DEBUG = True

ALLOWED_HOSTS = ['testes.escolajoseranieri.com.br', 'localhost', '127.0.0.1']

# Configuração do banco de dados para o ambiente de testes (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Motor do banco de dados
        'NAME': 'ranieri_staging_db',        # Nome do banco de dados de testes
        'USER': 'ranieri_staging_user',      # Usuário do banco de dados de testes
        'PASSWORD': 'Gsp@root2025',          # Senha do usuário de testes
        'HOST': 'localhost',                 # Host do banco de dados
        'PORT': '',                          # Porta do MySQL (vazio para padrão)
    }
}