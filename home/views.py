# ranieri_project/home/views.py

from django.shortcuts import render

# View da Página Inicial Pública
def home_view(request):
    return render(request, 'home.html')

