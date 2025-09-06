from django.views.generic import ListView
from core.models import SimCo_Receita

class SimCozinhaPageView(ListView):
    model = SimCo_Receita
    template_name = 'simcozinha_page.html'
    context_object_name = 'receitas'
    paginate_by = 10
    ordering = ['-inclusion_date']
