# brindialogando/views.py
from django.views.generic import TemplateView

class BrinDialogandoPageView(TemplateView):
    # Caminho do template: brindialogando/templates/brindialogando_page.html
    template_name = 'brindialogando_page.html'

