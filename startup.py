#!/usr/bin/env python3
"""
GapHunter - Startup script para Azure App Service
Este script inicia a aplicação FastAPI do backend
"""

import sys
import os

# Adicionar pasta backend ao Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Mudar diretório de trabalho para backend
os.chdir(backend_path)

# Importar e executar o startup do backend
if __name__ == "__main__":
    from startup import main
    main()

