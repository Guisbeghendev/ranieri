from django.db.models.signals import post_save, post_delete, m2m_changed
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
        Group.objects.get_or_create(name='fotografo')

        # Garante que o grupo 'admin' exista no sistema de Grupos do Django Auth.
        Group.objects.get_or_create(name='admin')

        # --- Criação dos AudienceGroups padrão (se não existirem) ---
        # A associação do usuário a esses AudienceGroups será feita via m2m_changed abaixo.
        AudienceGroup.objects.get_or_create(name='membro', defaults={'description': "Grupo de audiência para membros padrão"})
        AudienceGroup.objects.get_or_create(name='fotografo', defaults={'description': "Grupo de audiência para fotógrafos"})
        AudienceGroup.objects.get_or_create(name='admin', defaults={'description': "Grupo de audiência para administradores"})


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Garante que o perfil seja salvo ao salvar o usuário.
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance) # Cria o profile se ele não existir


@receiver(m2m_changed, sender=User.groups.through)
def update_user_flags_and_audience_groups_on_group_change(sender, instance, action, pk_set, **kwargs):
    """
    Atualiza as flags is_staff e is_photographer do usuário
    quando ele é adicionado ou removido dos grupos 'Admin' ou 'Fotógrafo' (auth.Group).
    Também sincroniza a associação do usuário com os AudienceGroups correspondentes.
    """
    # Recarrega o usuário para garantir que estamos trabalhando com a versão mais recente
    user = User.objects.get(pk=instance.pk)

    # Lógica para is_staff (acesso ao painel admin)
    is_admin_group_member = user.groups.filter(name='admin').exists()
    if user.is_staff != is_admin_group_member:
        user.is_staff = is_admin_group_member
        user.save(update_fields=['is_staff'])

    # Lógica para is_photographer (flag customizada)
    is_photographer_group_member = user.groups.filter(name='fotografo').exists()
    if hasattr(user, 'is_photographer') and user.is_photographer != is_photographer_group_member:
        user.is_photographer = is_photographer_group_member
        user.save(update_fields=['is_photographer'])
    elif hasattr(user, 'profile') and hasattr(user.profile, 'is_photographer') and user.profile.is_photographer != is_photographer_group_member:
        user.profile.is_photographer = is_photographer_group_member
        user.profile.save(update_fields=['is_photographer'])

    # NOVO: Lógica para sincronizar User.audience_groups com User.groups
    if action == "post_add":
        for group_pk in pk_set:
            auth_group = Group.objects.get(pk=group_pk)
            # Tenta encontrar ou criar o AudienceGroup correspondente
            audience_group, created = AudienceGroup.objects.get_or_create(name=auth_group.name)
            # Adiciona o usuário ao AudienceGroup
            user.audience_groups.add(audience_group)
    elif action == "post_remove":
        for group_pk in pk_set:
            auth_group = Group.objects.get(pk=group_pk)
            try:
                # Remove o usuário do AudienceGroup correspondente
                audience_group = AudienceGroup.objects.get(name=auth_group.name)
                user.audience_groups.remove(audience_group)
            except AudienceGroup.DoesNotExist:
                pass # O AudienceGroup não existe, nada a remover


# Sinais para sincronizar auth.Group com core.AudienceGroup
@receiver(post_save, sender=Group)
def sync_auth_group_to_audience_group(sender, instance, created, **kwargs):
    """
    Cria ou atualiza um core.AudienceGroup quando um auth.Group é salvo.
    Se o auth.Group é criado, cria um AudienceGroup correspondente.
    Se o auth.Group é atualizado, garante que um AudienceGroup com o mesmo nome exista.
    """
    AudienceGroup.objects.get_or_create(
        name=instance.name,
        defaults={'description': f"Grupo de audiência para {instance.name}"}
    )

@receiver(post_delete, sender=Group)
def delete_audience_group_on_auth_group_delete(sender, instance, **kwargs):
    """
    Deleta o core.AudienceGroup correspondente quando um auth.Group é deletado.
    """
    try:
        audience_group = AudienceGroup.objects.get(name=instance.name)
        audience_group.delete()
    except AudienceGroup.DoesNotExist:
        pass # Já deletado ou nunca existiu
