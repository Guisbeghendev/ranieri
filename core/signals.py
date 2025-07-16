# ranieri_project/core/signals.py

from django.db.models.signals import post_save, m2m_changed # Importa m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group # Importe Group
from .models import User, AudienceGroup, Profile # Importar os modelos do app 'core'

@receiver(post_save, sender=User)
def create_user_profile_and_add_to_groups(sender, instance, created, **kwargs):
    if created:
        # Cria o Profile para o novo usuário se ele ainda não existir
        Profile.objects.get_or_create(user=instance)

        # --- Criação e Associação do grupo 'membro' (Django Auth Group) ---
        # Garante que o grupo padrão 'membro' exista no sistema de Grupos do Django Auth
        membro_group, _ = Group.objects.get_or_create(name='membro')
        # Adiciona o usuário recém-criado ao grupo 'membro' do Django Auth
        instance.groups.add(membro_group)

        # --- Criação dos grupos 'fotografo' e 'admin' (Django Auth Group) ---
        # Garante que o grupo 'fotografo' exista no sistema de Grupos do Django Auth.
        fotografo_group, _ = Group.objects.get_or_create(name='fotografo')

        # Garante que o grupo 'admin' exista no sistema de Grupos do Django Auth.
        admin_group, _ = Group.objects.get_or_create(name='admin')

        # --- Criação e Associação do AudienceGroup 'membro' ---
        # Garante que o AudienceGroup 'membro' exista e adiciona o usuário a ele
        membro_audience_group, _ = AudienceGroup.objects.get_or_create(name='membro')
        instance.audience_groups.add(membro_audience_group) # Adiciona ao AudienceGroup 'membro'

        # --- Criação dos AudienceGroups 'fotografo' e 'admin' ---
        # Garante que o AudienceGroup 'fotografo' exista.
        fotografo_audience_group, _ = AudienceGroup.objects.get_or_create(name='fotografo')

        # Garante que o AudienceGroup 'admin' exista.
        admin_audience_group, _ = AudienceGroup.objects.get_or_create(name='admin')


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Garante que o perfil seja salvo ao salvar o usuário.
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance) # Cria o profile se ele não existir


@receiver(m2m_changed, sender=User.groups.through)
def update_user_flags_on_group_change(sender, instance, action, pk_set, **kwargs):
    """
    Atualiza as flags is_staff e is_photographer do usuário
    quando ele é adicionado ou removido dos grupos 'Admin' ou 'Fotógrafo'.
    """
    if action == "post_add" or action == "post_remove":
        # Recarrega o usuário para garantir que estamos trabalhando com a versão mais recente
        user = User.objects.get(pk=instance.pk)

        # Lógica para is_staff (acesso ao painel admin)
        # Se o usuário está no grupo 'Admin', is_staff deve ser True. Caso contrário, False.
        is_admin_group_member = user.groups.filter(name='Admin').exists()
        if user.is_staff != is_admin_group_member:
            user.is_staff = is_admin_group_member
            user.save(update_fields=['is_staff']) # Salva apenas o campo modificado

        # Lógica para is_photographer (flag customizada)
        # Se o usuário está no grupo 'Fotógrafo', is_photographer deve ser True. Caso contrário, False.
        is_photographer_group_member = user.groups.filter(name='Fotógrafo').exists()

        # Verifica se a flag 'is_photographer' existe no modelo User customizado
        # (Baseado em interações anteriores, assumimos que está no modelo User)
        if hasattr(user, 'is_photographer') and user.is_photographer != is_photographer_group_member:
            user.is_photographer = is_photographer_group_member
            user.save(update_fields=['is_photographer']) # Salva apenas o campo modificado
        # Se 'is_photographer' estiver no modelo Profile (caso alternativo, menos provável aqui)
        elif hasattr(user, 'profile') and hasattr(user.profile, 'is_photographer') and user.profile.is_photographer != is_photographer_group_member:
            user.profile.is_photographer = is_photographer_group_member
            user.profile.save(update_fields=['is_photographer']) # Salva apenas o campo modificado
