from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# CORRIGIDO: Importe o seu modelo User personalizado de core.models
from core.models import User
# Mantenha a importação de Group do Django Auth padrão, pois você não o personalizou
from django.contrib.auth.models import Group
from guardian.admin import GuardedModelAdminMixin # Mantenha esta importação se for usar em outros modelos

# Personaliza como os Usuários aparecem no Admin
# Temporariamente simplificado para garantir o registro.
# Podemos adicionar 'get_all_permissions' de volta depois de confirmar que o User aparece.
class CustomUserAdmin(BaseUserAdmin):
    pass # Por enquanto, apenas use as configurações padrão do BaseUserAdmin

# Personaliza como os Grupos aparecem no Admin
class CustomGroupAdmin(admin.ModelAdmin):
    # Mantém os campos padrão de nome e permissões globais
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Permissions', {'fields': ('permissions',)}), # Permissões padrão do Django
    )

# ATENÇÃO: AS CHAMADAS admin.site.unregister() E admin.site.register()
# FORAM REMOVIDAS DAQUI E MOVIDAS PARA accounts/apps.py NO MÉTODO ready()
# NÃO COLOQUE-AS DE VOLTA NESTE ARQUIVO.
