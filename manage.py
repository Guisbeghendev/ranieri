#!/usr/bin/env python
"""Utilitário de linha de comando do Django para tarefas administrativas."""
import os
import sys
from dotenv import load_dotenv

def main():
    """Executa tarefas administrativas."""
    # Carrega as variáveis de ambiente do arquivo .env
    # Isso deve ser feito ANTES de importar qualquer coisa do Django
    load_dotenv()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Você tem certeza de que ele está instalado e "
            "disponível na sua variável de ambiente PYTHONPATH? Você se "
            "esqueceu de ativar um ambiente virtual?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
