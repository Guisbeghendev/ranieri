import os
from django.db import models, transaction  # Importa transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.core.files.base import ContentFile
import io
import json

# Importa a tarefa Celery de processamento de imagem
# Importamos aqui para que o método save possa dispará-la.
from photographer.tasks import process_image_task


# Função para obter as opções de marca d'água dinamicamente
def get_watermark_choices():
    # Define o caminho completo para o diretório de marcas d'água
    watermark_dir = os.path.join(settings.MEDIA_ROOT, 'watermarks')

    # Opção padrão para "Sem Marca D'água"
    choices = [('', 'Sem Marca D\'água')]

    # Cria o diretório se ele não existir
    if not os.path.exists(watermark_dir):
        os.makedirs(watermark_dir)

    for filename in os.listdir(watermark_dir):
        # Verifica se é um arquivo de imagem
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Adiciona o nome do arquivo como opção (valor, label)
            # O label é formatado para ser mais legível
            choices.append((filename, filename.replace('_', ' ').replace('-', ' ').capitalize()))
    return choices


# --- Modelo User (Personalizado e Limpo) ---
class User(AbstractUser):
    # Sobrescrita de campos para evitar o related_name clash com AbstractUser
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('Grupos'),
        blank=True,
        help_text=(
            'Os grupos aos quais este usuário pertence. Um usuário terá todas as permissões '
            'concedidas a cada um de seus grupos.'
        ),
        related_name="core_user_groups_set",
        related_query_name="core_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('Permissões do Usuário'),
        blank=True,
        help_text=('Permissões específicas concedidas a este usuário.'),
        related_name="core_user_permissions_set",
        related_query_name="core_user_permission",
    )

    # --- Campo para os AudienceGroups do usuário ---
    audience_groups = models.ManyToManyField(
        'core.AudienceGroup',
        verbose_name="Grupos de Audiência",
        related_name='users',
        blank=True,
        help_text='Os grupos de audiência aos quais este usuário pertence para acesso a conteúdo.'
    )

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.username

    # MÉTODO CORRIGIDO: Verifica se o usuário pertence ao grupo 'fotografo' OU é superusuário
    @property
    def is_photographer(self):
        # Retorna True se for superusuário OU se pertencer ao grupo 'fotografo'
        return self.is_superuser or self.groups.filter(name='fotografo').exists()


# --- Modelo AudienceGroup ---
class AudienceGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome do Grupo de Audiência")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição do Grupo")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = 'Grupo de Audiência'
        verbose_name_plural = 'Grupos de Audiência'
        ordering = ['name']

    def __str__(self):
        return self.name


# --- Modelo Profile ---
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuário"
    )

    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Endereço")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Cidade")
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="Estado")
    whatsapp = models.CharField(max_length=30, null=True, blank=True, verbose_name="WhatsApp")
    other_contact = models.CharField(max_length=255, null=True, blank=True, verbose_name="Outro Contato")

    quem_sou_para_escola = models.TextField(null=True, blank=True, verbose_name="Quem sou para a Escola?")

    biography = models.TextField(null=True, blank=True, verbose_name="Biografia")
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True,
                                        verbose_name="Foto de Perfil")
    website = models.URLField(blank=True, null=True, verbose_name="Website / Portfólio")

    last_activity_date = models.DateTimeField(null=True, blank=True, verbose_name="Última Atividade")
    document_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="RA do Aluno")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user.username}'


# --- Modelo Galeria ---
class Galeria(models.Model):
    name = models.CharField(max_length=200, verbose_name="Título da Galeria")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição da Galeria")
    event_date = models.DateField(null=True, blank=True, verbose_name="Data do Evento")

    # Campo para a marca d'água selecionada (nome do arquivo)
    watermark_choice = models.CharField(
        max_length=100,
        choices=get_watermark_choices(),
        blank=True,
        verbose_name="Marca D'água",
        help_text="Selecione uma marca d'água para aplicar nas imagens desta galeria."
    )

    is_public = models.BooleanField(default=False, verbose_name="É Pública?")

    fotografo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_galleries',
        verbose_name="Fotógrafo Responsável"
    )

    cover_image = models.OneToOneField(
        'core.Image',
        on_delete=models.SET_NULL,
        related_name='gallery_cover',
        null=True,
        blank=True,
        verbose_name="Imagem de Capa"
    )

    audience_groups = models.ManyToManyField(
        'core.AudienceGroup',
        verbose_name="Grupos de Audiência",
        related_name='accessible_galleries',
        blank=True,
        help_text='Grupos de audiência que têm acesso a esta galeria.'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = 'Galeria'
        verbose_name_plural = 'Galerias'
        ordering = ['-event_date', '-created_at', 'name']
        permissions = (
            ("change_galeria_publicado", "Pode alterar status de publicação da galeria"),
        )

    def __str__(self):
        return self.name


# --- Modelo Image ---
class Image(models.Model):
    galeria = models.ForeignKey(
        'core.Galeria',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Galeria Associada"
    )

    image_file_original = models.ImageField(upload_to='galeria_images/originals/',
                                            verbose_name="Arquivo de Imagem Original")
    image_file_thumb = models.ImageField(upload_to='galeria_images/thumbnails/', null=True, blank=True,
                                         verbose_name="Thumbnail da Imagem")
    image_file_watermarked = models.ImageField(upload_to='galeria_images/watermarked/', blank=True, null=True,
                                               verbose_name="Com Marca D'água")

    original_file_name = models.CharField(max_length=255, blank=True, null=True,
                                          verbose_name="Nome Original do Arquivo")
    watermark_applied = models.BooleanField(default=False, verbose_name="Marca D'água Aplicada?")
    metadata = models.JSONField(null=True, blank=True, verbose_name="Metadados da Imagem")
    order = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name="Ordem de Exibição")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = 'Imagem'
        verbose_name_plural = 'Imagens'
        ordering = ['galeria', 'order', 'created_at']

    def __str__(self):
        return f"Imagem: {self.original_file_name or self.image_file_original.name.split('/')[-1]} (Galeria: {self.galeria.name})"

    # Override do método save para disparar a tarefa Celery
    def save(self, *args, **kwargs):
        # Flag para saber se é a primeira vez que o objeto está sendo salvo
        is_new_image = self._state.adding

        # Salva a instância primeiro. Isso é crucial para que o objeto tenha um PK
        # e o arquivo original esteja salvo no disco para a tarefa Celery.
        super().save(*args, **kwargs)

        # Dispara a tarefa Celery APENAS SE for uma nova imagem
        # OU se a imagem original existe mas as processadas (thumb/watermarked) ainda não foram geradas.
        # O uso de transaction.on_commit() garante que a tarefa só seja enviada
        # após a transação do banco de dados ser confirmada.
        if is_new_image or (self.image_file_original and not self.image_file_thumb and not self.image_file_watermarked):
            transaction.on_commit(lambda: process_image_task.delay(self.pk))
            print(f"Disparada tarefa Celery para processar imagem {self.pk} (após commit da transação).")

