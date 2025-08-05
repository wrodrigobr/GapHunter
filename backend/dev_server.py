#!/usr/bin/env python3
"""
Script de desenvolvimento para iniciar o servidor sem dependências de banco de dados
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório atual ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar variável de ambiente para modo de desenvolvimento
os.environ['DEV_MODE'] = 'true'

# Importar e criar o app FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="GapHunter API - Modo Desenvolvimento",
    description="API para análise técnica de mãos de poker (modo desenvolvimento)",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretório para uploads se não existir
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "GapHunter API - Modo Desenvolvimento", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "development"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API funcionando em modo desenvolvimento"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando GapHunter em modo desenvolvimento...")
    print("📡 Servidor disponível em: http://localhost:8000")
    print("📚 Documentação em: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 