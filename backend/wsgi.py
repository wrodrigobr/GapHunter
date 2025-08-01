#!/usr/bin/env python3
"""
WSGI entry point para Azure App Service
"""

import os
import sys

# Adicionar o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(__file__))

# Importar o aplicativo FastAPI
from app.main import app

# Para compatibilidade com WSGI
application = app 