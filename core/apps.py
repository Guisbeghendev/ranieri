# ranieri_project/core/apps.py

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        # Importa o módulo de signals para que os signals sejam registrados
        import core.signals

        # Importa o módulo de administração para que o Django o descubra
        # Esta linha garante que a classe de administração para Repertorio_Coral seja registrada.
        import core.admin
