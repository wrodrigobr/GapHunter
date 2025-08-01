#!/usr/bin/env python3
"""
Entry point para Azure App Service
"""

import os
import sys

# Adicionar o diretório atual ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar o aplicativo FastAPI
from app.main import app

# Para compatibilidade com WSGI
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 