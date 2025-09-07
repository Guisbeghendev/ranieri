import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente a partir do arquivo .env.
# Isso deve ser a primeira coisa a ser feita.
# A função irá procurar o arquivo na pasta onde o wsgi.py está.
load_dotenv()

# Define o caminho base do projeto, que é o diretório que contém este arquivo.
PROJECT_ROOT = Path(__file__).resolve().parent

# Adiciona o diretório raiz do projeto ao PATH do Python.
sys.path.insert(0, str(PROJECT_ROOT))

# Tenta carregar a configuração do ambiente usando uma variável de sistema.
# Se a variável 'DJANGO_SETTINGS_MODULE' não estiver definida,
# ele irá usar 'local.py' por padrão.
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'ranieri_project.settings.local')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# Agora sim, carrega a aplicação WSGI do Django.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
