from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = "Contas de Usuário" # Nome amigável para o Admin

    def ready(self):
        # Mova todas as importações de modelos e admin para DENTRO deste método.
        # Isso garante que elas só sejam executadas quando o Django App Registry estiver pronto.
        from django.contrib import admin
        # IMPORTANTE: Importe o seu modelo User personalizado de core.models
        from core.models import User
        # Mantenha a importação de Group do Django Auth padrão
        from django.contrib.auth.models import Group
        from .admin import CustomUserAdmin, CustomGroupAdmin

        # SOLUÇÃO: Removido o try/except para o registro do User
        # O User personalizado nunca é registrado automaticamente, então não precisa de unregister
        admin.site.register(User, CustomUserAdmin)

        # Mantenha o unregister e register para Group, pois Group é o padrão do Django
        try:
            admin.site.unregister(Group)
            admin.site.register(Group, CustomGroupAdmin)
        except admin.sites.NotRegistered:
            pass # Se Group ainda não estiver registrado, apenas ignore
