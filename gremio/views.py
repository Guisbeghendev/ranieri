# gremio/views.py
from django.views.generic import TemplateView

class GremioPageView(TemplateView):
    # Caminho do template: gremio/templates/gremio_page.html
    template_name = 'gremio_page.html'

