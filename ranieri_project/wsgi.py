"""
WSGI config for ranieri_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Define qual módulo de configurações o Django deve usar
# Se DJANGO_SETTINGS_MODULE não estiver definido, usa 'ranieri_project.settings.development' por padrão
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings.development')

application = get_wsgi_application()

