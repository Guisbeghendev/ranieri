from django import forms
from core.models import Galeria, Image, AudienceGroup, get_watermark_choices # Importe os modelos e a função necessários
from django.forms import inlineformset_factory

# Formulário para criar e editar galerias
class GalleryForm(forms.ModelForm):
    # Campos ManyToManyField como audience_groups são automaticamente renderizados como MultipleSelect
    # Você pode personalizar o widget se quiser uma interface diferente (ex: CheckboxSelectMultiple)
    audience_groups = forms.ModelMultipleChoiceField(
        queryset=AudienceGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple, # Exemplo: Usar checkboxes em vez de uma lista de seleção
        required=False,
        label="Grupos de Audiência"
    )

    class Meta:
        model = Galeria
        # NOVO: Adicionado 'watermark_choice' aos campos
        fields = ['name', 'description', 'event_date', 'watermark_choice', 'is_public', 'audience_groups']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}), # Widget para data
        }
        labels = {
            'name': 'Título da Galeria',
            'description': 'Descrição',
            'event_date': 'Data do Evento',
            'is_public': 'Tornar Pública?',
            # NOVO: Adicionado label para 'watermark_choice'
            'watermark_choice': 'Marca D\'água',
        }

# Formulário para upload de múltiplas imagens (não diretamente usado para FileField, mas para metadados)
# O upload de arquivos múltiplos será tratado diretamente na view.
class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['order', 'metadata'] # Campos que podem ser editados no formulário
        widgets = {
            'metadata': forms.Textarea(attrs={'rows': 3}), # Exemplo de widget para JSONField
        }
        labels = {
            'order': 'Ordem',
            'metadata': 'Metadados (JSON)',
        }

# ImageFormSet não será usado para upload inicial, mas pode ser útil para edição de imagens existentes
# ImageFormSet = inlineformset_factory(Galeria, Image, form=ImageForm, extra=1, can_delete=True)
