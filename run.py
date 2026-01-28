#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de execução rápida do Limpeza David
Permite executar o app diretamente da pasta raiz do projeto
"""

import os
import sys

# Adiciona o diretório do projeto ao path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Importa e executa o app
from app.main import main

if __name__ == "__main__":
    main()
