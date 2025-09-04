import os
# Importa todas as configurações do seu arquivo settings.py principal
from ranieri_project.settings.base import * # Acessa o arquivo base.py corretamente

# --- Configurações Específicas para Staging ---

# SECRET_KEY para segurança da aplicação.
# Adicionamos a lógica de leitura da variável de ambiente aqui,
# garantindo que o Django possa ler a chave do Apache.
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua_chave_de_desenvolvimento_aqui')

DEBUG = True

# A lista de hosts permitidos precisa incluir o nome de domínio que
# está sendo usado, 'staging.escolajoseranieri.com.br'.
ALLOWED_HOSTS = ['staging.escolajoseranieri.com.br', 'localhost', '127.0.0.1']

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
