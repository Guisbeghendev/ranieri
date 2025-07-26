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
site_packages_path = '/var/www/escolajoseranieri.com.br/html/venv/lib/python3.12/site-packages'
site.addsitedir(site_packages_path)

# Adiciona o diretório raiz do seu projeto Django ao sys.path.
sys.path.append('/var/www/escolajoseranieri.com.br/html')

# Adiciona o binário do python do venv ao PATH do sistema (importante para mod_wsgi).
os.environ['PATH'] = '/var/www/escolajoseranieri.com.br/html/venv/bin:' + os.environ.get('PATH', '')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
