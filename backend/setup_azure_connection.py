#!/usr/bin/env python3
"""
Script para configurar conexão com Azure SQL Database
"""

import os
from pathlib import Path

def setup_azure_connection():
    """Configura a conexão com Azure SQL Database"""
    
    print("🔧 CONFIGURAÇÃO DO AZURE SQL DATABASE")
    print("=" * 50)
    
    # Verificar se .env já existe
    env_path = Path(__file__).parent / ".env"
    
    if env_path.exists():
        print("📝 Arquivo .env já existe!")
        print("💡 Se precisar reconfigurar, delete o arquivo .env e execute novamente")
        return
    
    print("📝 Configurando arquivo .env...")
    print("🔗 Digite as informações do seu Azure SQL Database:")
    
    # Coletar informações
    server = input("🌐 Server (ex: gaphunter-server.database.windows.net): ").strip()
    database = input("🗄️  Database name: ").strip()
    username = input("👤 Username: ").strip()
    password = input("🔒 Password: ").strip()
    
    if not all([server, database, username, password]):
        print("❌ Todas as informações são obrigatórias!")
        return
    
    # Criar arquivo .env
    env_content = f"""# Configurações do Azure SQL Database
DB_SERVER={server}
DB_NAME={database}
DB_USERNAME={username}
DB_PASSWORD={password}
"""
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado com sucesso!")
        print(f"📁 Localização: {env_path}")
        
        # Testar conexão
        print("\n🧪 Testando conexão...")
        test_connection(server, database, username, password)
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")

def test_connection(server, database, username, password):
    """Testa a conexão com Azure SQL"""
    
    try:
        import pyodbc
        
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        
        print(f"🔗 Conectando a {server}/{database}...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        print("✅ Conexão bem-sucedida!")
        print(f"📋 SQL Server Version: {version[:100]}...")
        
        # Verificar tabelas
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'hands'")
        hands_count = cursor.fetchone()[0]
        
        if hands_count > 0:
            print(f"✅ Tabela 'hands' encontrada!")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM hands")
            total_hands = cursor.fetchone()[0]
            print(f"📊 Total de mãos: {total_hands}")
        else:
            print("⚠️  Tabela 'hands' não encontrada")
        
        conn.close()
        
    except ImportError:
        print("❌ pyodbc não instalado. Execute: pip install pyodbc")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("💡 Verifique:")
        print("   - Credenciais corretas")
        print("   - Firewall do Azure configurado")
        print("   - Driver ODBC instalado")

if __name__ == "__main__":
    setup_azure_connection() 