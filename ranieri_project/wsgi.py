"""
WSGI config for ranieri_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import site

# Adiciona o caminho do site-packages do seu ambiente virtual (venv) ao sys.path.
# Isso é crucial para que o mod_wsgi encontre o Django e suas dependências.
# Verifique se 'python3.12' é a versão correta do Python no seu venv.
# Para confirmar: ls /var/www/escolajoseranieri.com.br/venv/lib/
site_packages_path = '/var/www/escolajoseranieri.com.br/venv/lib/python3.12/site-packages'
site.addsitedir(site_packages_path)

# Adiciona o diretório raiz do seu projeto Django ao sys.path.
# Isso permite que o Django encontre seus próprios módulos e apps.
sys.path.append('/var/www/escolajoseranieri.com.br/html')


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
