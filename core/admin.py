from django.contrib import admin
from guardian.admin import GuardedModelAdminMixin
# Importe Galeria e AudienceGroup, pois Galeria tem um ManyToManyField para AudienceGroup
from .models import Galeria, AudienceGroup, Repertorio

# Registra o modelo Galeria no Django Admin
@admin.register(Galeria)
class GaleriaAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    # Usando os nomes de campo EXATOS do seu modelo Galeria
    list_display = ('name', 'event_date', 'is_public', 'fotografo', 'created_at')
    list_filter = ('is_public', 'event_date', 'fotografo', 'audience_groups') # Adicionado audience_groups ao filtro
    search_fields = ('name', 'description') # Usando 'name' e 'description'
    raw_id_fields = ('fotografo',) # 'fotografo' é o seu ForeignKey para o usuário
    # Se você quiser adicionar os grupos de audiência para edição direta na galeria
    filter_horizontal = ('audience_groups',)

# --- NOVO REGISTRO: Repertorio ---
@admin.register(Repertorio)
class RepertorioAdmin(admin.ModelAdmin):
    list_display = ('title', 'composer', 'inclusion_year', 'created_at')
    list_filter = ('inclusion_year',)
    search_fields = ('title', 'composer')
    list_per_page = 25

