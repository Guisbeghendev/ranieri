# simcozinha/views.py
from django.views.generic import TemplateView

class SimCozinhaPageView(TemplateView):
    # Caminho do template: simcozinha/templates/simcozinha_page.html
    template_name = 'simcozinha_page.html'

