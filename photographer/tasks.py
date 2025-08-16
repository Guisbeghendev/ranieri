import os
import io
from PIL import Image as PillowImage, ImageOps  # Importa ImageOps para exif_transpose
from django.core.files.base import ContentFile
from django.conf import settings
from celery import shared_task
import logging  # Importa o módulo de logging

# Configura o logger para esta tarefa
logger = logging.getLogger(__name__)

# Definir tamanhos máximos para as imagens, conforme sua especificação
DISPLAY_MAX_SIZE = (1920, 1920)  # Largura e altura máximas para a versão de display (com marca d'água)
THUMBNAIL_MAX_SIZE = (300, 300)  # Largura e altura máximas para a miniatura


@shared_task(bind=True, max_retries=5, default_retry_delay=30, time_limit=300, soft_time_limit=240)
def process_image_task(self, image_pk):
    """
    Tarefa Celery para processar uma imagem:
    1. Redimensionar para o tamanho de display (1920px no lado mais longo).
    2. Aplicar marca d'água (se selecionada).
    3. Gerar thumbnail (300px no lado mais longo).
    4. Corrigir orientação EXIF.
    5. Remover o arquivo de imagem original do disco após o processamento.
    """
    # Importa os modelos aqui dentro da tarefa para evitar problemas de importação circular
    from core.models import Image, Galeria

    try:
        logger.info(
            f"Tarefa: Iniciando processamento para imagem PK {image_pk} (tentativa {self.request.retries + 1}).")
        image_instance = Image.objects.get(pk=image_pk)

        # Obtém o caminho do arquivo original. Se não houver, ou não existir no disco, loga e sai.
        original_image_path = image_instance.image_file_original.path if image_instance.image_file_original else None

        if not original_image_path or not os.path.exists(original_image_path):
            logger.warning(
                f"Tarefa: Imagem original não encontrada ou caminho inválido para PK {image_pk}. Pulando processamento.")
            return

        img = None  # Inicializa 'img' para garantir escopo

        try:
            # Abre a imagem original. Usa 'with' para garantir que o arquivo seja fechado.
            with PillowImage.open(original_image_path) as original_img:
                logger.info(
                    f"Tarefa: Imagem original {original_image_path} aberta para PK {image_pk}.")

                # PASSO 1: Corrigir a orientação EXIF (se necessário) e normalizar a imagem
                # Esta é a solução robusta para o problema de "tombar" fotos.
                img = ImageOps.exif_transpose(original_img)
                logger.info(f"Tarefa: Orientação EXIF corrigida para PK {image_pk}.")

                needs_save = False  # Flag para controlar se precisamos salvar a instância no final

                # PASSO 2: Geração do Thumbnail
                # Gera o thumbnail apenas se ainda não existe
                if not image_instance.image_file_thumb:
                    try:
                        img_thumb = img.copy()  # Trabalha com uma cópia para não afetar a imagem principal
                        # Redimensiona para o tamanho máximo do thumbnail, mantendo a proporção
                        img_thumb.thumbnail(THUMBNAIL_MAX_SIZE, PillowImage.Resampling.LANCZOS)

                        thumb_io = io.BytesIO()
                        # Salva o thumbnail sempre como JPEG para otimização, com qualidade 75
                        img_thumb.convert("RGB").save(thumb_io, format='JPEG', quality=75, exif=b'')

                        thumb_filename = os.path.basename(image_instance.image_file_original.name)
                        name, ext = os.path.splitext(thumb_filename)
                        thumb_filename = f"{name}_thumb.jpeg"  # Garante extensão JPG

                        # Salva o arquivo no campo do modelo sem salvar no banco de dados ainda
                        image_instance.image_file_thumb.save(thumb_filename, ContentFile(thumb_io.getvalue()),
                                                             save=False)
                        thumb_io.close()  # Fecha o BytesIO para liberar memória
                        needs_save = True
                        logger.info(f"Tarefa: Thumbnail gerada para imagem {image_pk}.")

                    except Exception as e:
                        logger.error(
                            f"Tarefa: Erro ao gerar thumbnail para {image_instance.original_file_name} (PK: {image_pk}): {e}",
                            exc_info=True)
                        # O campo permanecerá vazio se a geração falhou, e o template exibirá o placeholder.

                # PASSO 3: Aplicação da Marca D'água ou Cópia para o campo watermarked (versão de display)
                # Processa apenas se o campo watermarked estiver vazio
                if not image_instance.image_file_watermarked:
                    gallery = image_instance.galeria  # Pega a galeria associada

                    # Redimensionar a imagem principal para o tamanho de display ANTES de aplicar a marca d'água
                    img_display = img.copy()
                    img_display.thumbnail(DISPLAY_MAX_SIZE, PillowImage.Resampling.LANCZOS)
                    logger.info(
                        f"Tarefa: Imagem redimensionada para display ({DISPLAY_MAX_SIZE[0]}px) para PK {image_pk}.")

                    if gallery.watermark_choice:
                        watermark_filename = gallery.watermark_choice
                        watermark_path = os.path.join(settings.MEDIA_ROOT, 'watermarks', watermark_filename)

                        if os.path.exists(watermark_path):
                            try:
                                # Usa a imagem já redimensionada para display
                                original_img_watermark = img_display.convert(
                                    "RGBA")  # Converte para RGBA para aplicar marca d'água
                                with PillowImage.open(watermark_path) as watermark_img_file:
                                    watermark_img = watermark_img_file.convert("RGBA")

                                margin = 20  # Margem em pixels do canto
                                watermark_width_percent = 0.20  # Marca d'água terá 20% da largura da imagem de display
                                opacity = 0.8  # Opacidade ajustada para 80%

                                # Redimensiona a marca d'água proporcionalmente
                                base_width = int(original_img_watermark.width * watermark_width_percent)
                                w_percent = (base_width / float(watermark_img.size[0]))
                                h_size = int((float(watermark_img.size[1]) * float(w_percent)))
                                watermark_img = watermark_img.resize((base_width, h_size),
                                                                     PillowImage.Resampling.LANCZOS)

                                # Aplica opacidade ao canal alfa da marca d'água
                                alpha_channel = watermark_img.split()[3]
                                alpha_channel = alpha_channel.point(lambda i: i * opacity)
                                watermark_img.putalpha(alpha_channel)

                                # Posição da marca d'água no canto inferior direito
                                position = (original_img_watermark.width - watermark_img.width - margin,
                                            original_img_watermark.height - watermark_img.height - margin)

                                # Cria uma camada transparente e cola a marca d'água nela
                                transparent_layer = PillowImage.new('RGBA', original_img_watermark.size, (0, 0, 0, 0))
                                transparent_layer.paste(watermark_img, position, watermark_img)

                                # Combina a imagem original com a camada da marca d'água
                                watermarked_output = PillowImage.alpha_composite(original_img_watermark,
                                                                                 transparent_layer)

                                watermarked_io = io.BytesIO()
                                # Salva como JPEG, mesmo que a original fosse PNG, para otimização
                                watermarked_output.convert("RGB").save(watermarked_io, format='JPEG', quality=75,
                                                                       exif=b'')

                                watermarked_filename = os.path.basename(image_instance.image_file_original.name)
                                name, ext = os.path.splitext(watermarked_filename)
                                watermarked_filename = f"{name}_watermarked.jpeg"  # Garante extensão JPG

                                image_instance.image_file_watermarked.save(watermarked_filename,
                                                                           ContentFile(watermarked_io.getvalue()),
                                                                           save=False)
                                watermarked_io.close()  # Fecha o BytesIO
                                image_instance.watermark_applied = True
                                needs_save = True
                                logger.info(f"Tarefa: Marca d'água aplicada para imagem {image_pk}.")

                            except Exception as e:
                                logger.error(
                                    f"Tarefa: Erro ao aplicar marca d'água para {image_instance.original_file_name} (PK: {image_pk}): {e}",
                                    exc_info=True)
                                image_instance.watermark_applied = False  # Mantém como False para indicar falha
                        else:
                            logger.warning(
                                f"Tarefa: Arquivo de marca d'água não encontrado: {watermark_path} para imagem {image_pk}.")
                            image_instance.watermark_applied = False
                    else:  # Nenhuma marca d'água escolhida, copia a versão de display para o campo watermarked
                        try:
                            no_watermark_io = io.BytesIO()
                            # Salva a versão de display como JPEG, sem marca d'água
                            img_display.convert("RGB").save(no_watermark_io, format='JPEG', quality=75, exif=b'')

                            original_filename = os.path.basename(image_instance.image_file_original.name)
                            name, ext = os.path.splitext(original_filename)
                            original_filename_copy = f"{name}.jpeg"  # Garante extensão JPG

                            image_instance.image_file_watermarked.save(original_filename_copy,
                                                                       ContentFile(no_watermark_io.getvalue()),
                                                                       save=False)
                            no_watermark_io.close()  # Fecha o BytesIO
                            image_instance.watermark_applied = False  # Nenhuma marca d'água foi realmente aplicada
                            needs_save = True
                            logger.info(
                                f"Tarefa: Imagem redimensionada (sem marca d'água) copiada para campo watermarked para imagem {image_pk}.")
                        except Exception as e:
                            logger.error(
                                f"Tarefa: Erro ao copiar imagem redimensionada para watermarked (sem marca d'água) para {image_instance.original_file_name} (PK: {image_pk}): {e}",
                                exc_info=True)
                            image_instance.watermark_applied = False

                # Salva a instância da imagem no banco de dados se houver alterações nos campos processados
                if needs_save:
                    image_instance.save(
                        update_fields=['image_file_thumb', 'image_file_watermarked', 'watermark_applied'])
                    logger.info(f"Tarefa: Imagem {image_pk} processada e salva com sucesso.")

                    # PASSO FINAL: Remover o arquivo original do disco
                    if original_image_path and os.path.exists(original_image_path):
                        try:
                            os.remove(original_image_path)
                            # Limpa o campo no modelo APENAS depois de remover o arquivo
                            # O 'delete(save=False)' apenas remove a referência do FileField,
                            # o 'save()' subsequente persiste essa mudança no banco de dados.
                            image_instance.image_file_original.delete(save=False)
                            image_instance.save(update_fields=['image_file_original'])  # Salva a alteração do campo
                            logger.info(
                                f"Tarefa: Arquivo original {original_image_path} removido do disco para PK {image_pk}.")
                        except Exception as e:
                            logger.error(
                                f"Tarefa: Erro ao remover arquivo original {original_image_path} para PK {image_pk}: {e}",
                                exc_info=True)
                else:
                    logger.info(f"Tarefa: Nenhuma alteração de processamento necessária para imagem {image_pk}.")

        except Image.DoesNotExist:
            logger.warning(
                f"Tarefa: Imagem com PK {image_pk} não encontrada. Pode ter sido deletada ou ainda não commitada. Re-tentando ({self.request.retries + 1}/{self.max_retries})...")
            # Re-tenta a tarefa se a imagem não for encontrada, útil para problemas de transação.
            raise self.retry(exc=Image.DoesNotExist(), countdown=5)
        except Exception as e:
            logger.error(f"Tarefa: Erro inesperado ao processar imagem {image_pk}: {e}",
                         exc_info=True)  # Loga o traceback completo
            # Re-lança a exceção para que o Celery marque a tarefa como falha e tente novamente
            raise self.retry(exc=e, countdown=60)  # Tenta novamente em 60 segundos para erros gerais
    except Exception as e:
        logger.critical(f"Tarefa: Erro crítico antes mesmo de obter a instância da imagem para PK {image_pk}: {e}",
                        exc_info=True)
        # Se falhar antes mesmo de obter a instância da imagem, é um problema crítico de configuração.
        # Considera não tentar novamente indefinidamente ou escalar.
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        else:
            logger.critical(f"Tarefa: Falha final para imagem {image_pk} após {self.max_retries} tentativas.")
            raise  # Re-lança a exceção para marcar a tarefa como falha permanente
