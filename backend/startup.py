#!/usr/bin/env python3
"""
Script de inicialização para produção do GapHunter
Executa migrações do banco de dados e inicia o servidor
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído com sucesso")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Iniciando GapHunter em modo produção...")
    
    # Carregar variáveis de ambiente
    if os.path.exists('.env.production'):
        load_dotenv('.env.production')
        print("✅ Carregadas variáveis de ambiente de produção")
    else:
        load_dotenv()
        print("⚠️  Usando variáveis de ambiente padrão")
    
    # Verificar variáveis essenciais
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não configurada!")
        sys.exit(1)
    
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        print("❌ SECRET_KEY não configurada!")
        sys.exit(1)
    
    print(f"📊 Banco de dados: {database_url.split('@')[0]}@***")
    
    # Executar migrações do banco de dados
    if not run_command("alembic upgrade head", "Executando migrações do banco de dados"):
        print("❌ Falha nas migrações. Tentando criar migração inicial...")
        if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Criando migração inicial"):
            sys.exit(1)
        if not run_command("alembic upgrade head", "Aplicando migração inicial"):
            sys.exit(1)
    
    # Criar diretórios necessários
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    print("✅ Diretórios criados")
    
    # Verificar se é ambiente de desenvolvimento ou produção
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if environment == 'production':
        print("🌐 Iniciando servidor em modo produção com Gunicorn...")
        
        # Configurações do Gunicorn para produção
        gunicorn_cmd = [
            "gunicorn",
            "app.main:app",
            "-w", "4",  # 4 workers
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", "0.0.0.0:8000",
            "--timeout", "120",
            "--keep-alive", "5",
            "--max-requests", "1000",
            "--max-requests-jitter", "100",
            "--access-logfile", "logs/access.log",
            "--error-logfile", "logs/error.log",
            "--log-level", "info"
        ]
        
        try:
            subprocess.run(gunicorn_cmd, check=True)
        except KeyboardInterrupt:
            print("\n🛑 Servidor interrompido pelo usuário")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            sys.exit(1)
    
    else:
        print("🔧 Iniciando servidor em modo desenvolvimento...")
        try:
            subprocess.run([
                "uvicorn", 
                "app.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000", 
                "--reload"
            ], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Servidor interrompido pelo usuário")

if __name__ == "__main__":
    main()

