# Generated by Django 5.2.4 on 2025-07-10 01:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='galeria',
            options={'ordering': ['-event_date', '-created_at', 'name'], 'permissions': (('change_galeria_publicado', 'Pode alterar status de publicação da galeria'),), 'verbose_name': 'Galeria', 'verbose_name_plural': 'Galerias'},
        ),
    ]
