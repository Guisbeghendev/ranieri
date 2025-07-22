"""
WSGI config for ranieri_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
# Importe load_dotenv para carregar o arquivo .env
from dotenv import load_dotenv # ADICIONE ESTA LINHA

# Define o caminho para o arquivo .env na raiz do projeto
# Isso garante que o .env seja carregado antes que o Django tente acessar as variáveis
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path) # Carrega as variáveis do .env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings')

application = get_wsgi_application()
