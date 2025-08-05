#!/usr/bin/env python3
"""
Script de inicialização para produção do GapHunter
Executa migrações do banco de dados e inicia o servidor
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Adicionar o diretório atual ao path do Python para garantir imports corretos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

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
    
    # Verificar se é SQL Server e se drivers estão disponíveis
    if 'mssql' in database_url or 'pyodbc' in database_url:
        try:
            import pyodbc
            print("🔍 Testando conectividade com SQL Server...")
            
            # Tentar diferentes configurações de conexão
            connection_configs = [
                {
                    'timeout': 30,
                    'connect_timeout': 30,
                    'login_timeout': 30
                },
                {
                    'timeout': 60,
                    'connect_timeout': 60,
                    'login_timeout': 60
                },
                {
                    'timeout': 120,
                    'connect_timeout': 120,
                    'login_timeout': 120
                }
            ]
            
            success = False
            for i, config in enumerate(connection_configs):
                try:
                    print(f"🔄 Tentativa {i+1} com timeout {config['timeout']}s...")
                    
                    import sqlalchemy
                    from sqlalchemy import create_engine
                    
                    test_engine = create_engine(
                        database_url,
                        connect_args=config
                    )
                    
                    with test_engine.connect() as conn:
                        conn.execute(sqlalchemy.text("SELECT 1"))
                        print(f"✅ Conexão com SQL Server bem-sucedida (tentativa {i+1})")
                        success = True
                        break
                        
                except Exception as e:
                    print(f"❌ Tentativa {i+1} falhou: {str(e)[:100]}...")
                    continue
            
            if not success:
                print("⚠️  Todas as tentativas de conexão com SQL Server falharam")
                print("🔄 Usando SQLite como fallback...")
                os.environ['DATABASE_URL'] = 'sqlite:///./gaphunter.db'
                database_url = 'sqlite:///./gaphunter.db'
                
        except ImportError:
            print("⚠️  Drivers SQL Server não disponíveis, usando SQLite como fallback...")
            os.environ['DATABASE_URL'] = 'sqlite:///./gaphunter.db'
            database_url = 'sqlite:///./gaphunter.db'
    
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
        print("🌐 Iniciando servidor em modo produção...")
        
        # Para Azure App Service, usar configuração mais simples
        # Verificar se Gunicorn está disponível
        try:
            subprocess.run(["gunicorn", "--version"], check=True, capture_output=True)
            print("✅ Gunicorn disponível, usando Gunicorn...")
            
            # Configurações simplificadas do Gunicorn para Azure
            gunicorn_cmd = [
                "gunicorn",
                "backend.app.main:app",  # Usar app.py como entry point
                "-w", "1",  # 1 worker para evitar problemas de memória
                "-k", "uvicorn.workers.UvicornWorker",
                "--bind", "0.0.0.0:8000",
                "--timeout", "300",  # Timeout maior para Azure
                "--log-level", "info",
                "--access-logfile", "-",  # Log para stdout
                "--error-logfile", "-"   # Log para stderr
            ]
            
            subprocess.run(gunicorn_cmd, check=True)
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Gunicorn não disponível, usando Uvicorn...")
            
            # Fallback para Uvicorn se Gunicorn falhar
            subprocess.run([
                "uvicorn", 
                "backend.app.main:app",  # Usar app.py como entry point
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--log-level", "info"
            ], check=True)
    
    else:
        print("🔧 Iniciando servidor em modo desenvolvimento...")
        try:
            subprocess.run([
                "uvicorn", 
                "backend.app.main:app",  # Usar app.py como entry point
                "--host", "0.0.0.0", 
                "--port", "8000", 
                "--reload"
            ], check=True)
        except KeyboardInterrupt:
            print("\n🛑 Servidor interrompido pelo usuário")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

