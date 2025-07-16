import os
import io
from PIL import Image as PillowImage, ImageOps  # Importa ImageOps para exif_transpose
from django.core.files.base import ContentFile
from django.conf import settings
from celery import shared_task
import logging  # Importa o módulo de logging

# Configura o logger para esta tarefa
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=30, time_limit=300, soft_time_limit=240)
def process_image_task(self, image_pk):
    """
    Tarefa Celery para processar uma imagem: gerar thumbnail, aplicar marca d'água
    e garantir a orientação correta.
    Adicionado tratamento de erros mais robusto e otimizações para grandes volumes.
    """
    # Importa os modelos aqui dentro da tarefa para evitar problemas de importação circular
    from core.models import Image, Galeria

    try:
        logger.info(
            f"Tarefa: Iniciando processamento para imagem PK {image_pk} (tentativa {self.request.retries + 1}).")
        image_instance = Image.objects.get(pk=image_pk)

        # Verifica se o arquivo original existe no disco antes de tentar abri-lo
        if not image_instance.image_file_original or not os.path.exists(image_instance.image_file_original.path):
            logger.warning(
                f"Tarefa: Imagem original não encontrada ou caminho inválido para PK {image_pk}. Pulando processamento.")
            return

        img = None  # Inicializa 'img' fora do bloco 'with' para que possa ser acessado

        try:
            # Usa 'with' statement para garantir que o arquivo de imagem seja fechado corretamente
            with PillowImage.open(image_instance.image_file_original.path) as original_img:
                logger.info(
                    f"Tarefa: Imagem original {image_instance.image_file_original.path} aberta para PK {image_pk}.")

                # PASSO 1: Corrigir a orientação EXIF (se necessário) e normalizar a imagem
                # Esta é a solução robusta para o problema de "tombar"
                img = ImageOps.exif_transpose(original_img)
                logger.info(f"Tarefa: Orientação EXIF corrigida para PK {image_pk}.")

                needs_save = False  # Flag para controlar se precisamos salvar a instância no final

                # PASSO 2: Geração do Thumbnail
                # Gera o thumbnail apenas se ainda não existe
                if not image_instance.image_file_thumb:
                    try:
                        img_thumb = img.copy()  # Trabalha com uma cópia para não afetar a imagem principal
                        # Use PillowImage.Resampling.LANCZOS para melhor qualidade e compatibilidade
                        img_thumb.thumbnail((300, 300), PillowImage.Resampling.LANCZOS)

                        thumb_io = io.BytesIO()
                        # Determina o formato de saída para o thumbnail
                        if img_thumb.mode in ('RGBA', 'P') or (img_thumb.info and 'transparency' in img_thumb.info):
                            format_thumb = 'PNG'
                        else:
                            format_thumb = 'JPEG'

                        # Salva o thumbnail, removendo todos os metadados EXIF para reduzir tamanho e evitar problemas
                        img_thumb.save(thumb_io, format=format_thumb, quality=85, exif=b'')

                        thumb_filename = os.path.basename(image_instance.image_file_original.name)
                        name, ext = os.path.splitext(thumb_filename)
                        thumb_filename = f"{name}_thumb.{format_thumb.lower()}"

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
                        # Não defina como None aqui; o campo permanecerá vazio se a geração falhou,
                        # e o template exibirá o placeholder.

                # PASSO 3: Aplicação da Marca D'água ou Cópia para o campo watermarked
                # Processa apenas se o campo watermarked estiver vazio
                if not image_instance.image_file_watermarked:
                    gallery = image_instance.galeria  # Pega a galeria associada
                    if gallery.watermark_choice:
                        watermark_filename = gallery.watermark_choice
                        watermark_path = os.path.join(settings.MEDIA_ROOT, 'watermarks', watermark_filename)

                        if os.path.exists(watermark_path):
                            try:
                                original_img_watermark = img.copy().convert("RGBA")  # Usa a imagem já transposta
                                with PillowImage.open(watermark_path) as watermark_img_file:
                                    watermark_img = watermark_img_file.convert("RGBA")

                                margin = 20  # Margem em pixels do canto
                                watermark_width_percent = 0.20  # Marca d'água terá 20% da largura da imagem original
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

                                # CORREÇÃO CRÍTICA: Posição da marca d'água no canto inferior direito
                                position = (original_img_watermark.width - watermark_img.width - margin,
                                            original_img_watermark.height - watermark_img.height - margin)

                                # Cria uma camada transparente e cola a marca d'água nela
                                transparent_layer = PillowImage.new('RGBA', original_img_watermark.size, (0, 0, 0, 0))
                                transparent_layer.paste(watermark_img, position, watermark_img)

                                # Combina a imagem original com a camada da marca d'água
                                watermarked_output = PillowImage.alpha_composite(original_img_watermark,
                                                                                 transparent_layer)

                                watermarked_io = io.BytesIO()
                                # Determina o formato de saída para a imagem com marca d'água
                                if watermarked_output.mode == 'RGBA':
                                    format_watermarked = 'PNG'
                                else:
                                    format_watermarked = 'JPEG'

                                # Salva a imagem com marca d'água, removendo todos os metadados EXIF
                                watermarked_output.save(watermarked_io, format=format_watermarked, quality=90, exif=b'')

                                watermarked_filename = os.path.basename(image_instance.image_file_original.name)
                                name, ext = os.path.splitext(watermarked_filename)
                                watermarked_filename = f"{name}_watermarked.{format_watermarked.lower()}"

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
                    else:  # Nenhuma marca d'água escolhida, copia a original para o campo watermarked
                        try:
                            # Usa a imagem já transposta
                            original_img_no_watermark = img.copy()
                            no_watermark_io = io.BytesIO()
                            if original_img_no_watermark.mode in ('RGBA', 'P') or (
                                    original_img_no_watermark.info and 'transparency' in original_img_no_watermark.info):
                                format_no_watermark = 'PNG'
                            else:
                                format_no_watermark = 'JPEG'
                            # Salva a imagem, removendo todos os metadados EXIF
                            original_img_no_watermark.save(no_watermark_io, format=format_no_watermark, quality=90,
                                                           exif=b'')

                            original_filename = os.path.basename(image_instance.image_file_original.name)
                            name, ext = os.path.splitext(original_filename)
                            original_filename_copy = f"{name}.{format_no_watermark.lower()}"

                            image_instance.image_file_watermarked.save(original_filename_copy,
                                                                       ContentFile(no_watermark_io.getvalue()),
                                                                       save=False)
                            no_watermark_io.close()  # Fecha o BytesIO
                            image_instance.watermark_applied = False  # Nenhuma marca d'água foi realmente aplicada
                            needs_save = True
                            logger.info(
                                f"Tarefa: Imagem original copiada para campo watermarked (sem marca d'água) para imagem {image_pk}.")
                        except Exception as e:
                            logger.error(
                                f"Tarefa: Erro ao copiar imagem original para watermarked (sem marca d'água) para {image_instance.original_file_name} (PK: {image_pk}): {e}",
                                exc_info=True)
                            image_instance.watermark_applied = False

                # Salva a instância da imagem no banco de dados se houver alterações nos campos processados
                if needs_save:
                    image_instance.save(
                        update_fields=['image_file_thumb', 'image_file_watermarked', 'watermark_applied'])
                    logger.info(f"Tarefa: Imagem {image_pk} processada e salva com sucesso.")
                else:
                    logger.info(f"Tarefa: Nenhuma alteração de processamento necessária para imagem {image_pk}.")

        except Image.DoesNotExist:
            logger.warning(
                f"Tarefa: Imagem com PK {image_pk} não encontrada. Pode ter sido deletada ou ainda não commitada. Re-tentando ({self.request.retries + 1}/{self.max_retries})...")
            # CORREÇÃO CRÍTICA AQUI: Passar uma INSTÂNCIA da exceção, não a CLASSE
            raise self.retry(exc=Image.DoesNotExist(), countdown=5)  # Tenta novamente em 5 segundos
        except Exception as e:
            logger.error(f"Tarefa: Erro inesperado ao processar imagem {image_pk}: {e}",
                         exc_info=True)  # Loga o traceback completo
            # Re-lança a exceção para que o Celery marque a tarefa como falha e tente novamente
            # CORREÇÃO CRÍTICA AQUI: Passar uma INSTÂNCIA da exceção, não a CLASSE
            raise self.retry(exc=e, countdown=60)  # Tenta novamente em 60 segundos para erros gerais
    except Exception as e:
        logger.critical(f"Tarefa: Erro crítico antes mesmo de iniciar o processamento para imagem {image_pk}: {e}",
                        exc_info=True)
        # Se falhar antes mesmo de obter a instância da imagem, é um problema crítico de configuração.
        # Considera não tentar novamente indefinidamente ou escalar.
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        else:
            logger.critical(f"Tarefa: Falha final para imagem {image_pk} após {self.max_retries} tentativas.")
            raise  # Re-lança a exceção para marcar a tarefa como falha permanente
