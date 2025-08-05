#!/usr/bin/env python3
"""
Script para executar a migration da tabela hand_actions no SQL Server
"""

import pyodbc
import os
from pathlib import Path
from dotenv import load_dotenv

def run_sql_server_migration():
    """Executa a migration para criar a tabela hand_actions no SQL Server"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações do banco SQL Server
    server = os.getenv('DB_SERVER', 'localhost')
    database = os.getenv('DB_NAME', 'gaphunter')
    username = os.getenv('DB_USERNAME', 'sa')
    password = os.getenv('DB_PASSWORD', '')
    
    # String de conexão
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    
    # Caminho para o arquivo de migration
    migration_path = Path(__file__).parent / "migrations" / "003_add_hand_actions_table.sql"
    
    if not migration_path.exists():
        print(f"❌ Arquivo de migration não encontrado: {migration_path}")
        return False
    
    try:
        # Conectar ao SQL Server
        print(f"🔗 Conectando ao SQL Server: {server}/{database}")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print(f"✅ Conectado com sucesso!")
        
        # Ler o arquivo de migration
        with open(migration_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print(f"📄 Migration carregada: {migration_path}")
        
        # Executar a migration
        print("🚀 Executando migration...")
        
        # Dividir o SQL em comandos individuais
        commands = migration_sql.split(';')
        
        for i, command in enumerate(commands):
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    print(f"✅ Comando {i+1} executado com sucesso")
                except pyodbc.Error as e:
                    if "already exists" in str(e):
                        print(f"⚠️  Comando {i+1}: {e}")
                    else:
                        print(f"❌ Erro no comando {i+1}: {e}")
                        raise
        
        # Commit das alterações
        conn.commit()
        print("💾 Alterações salvas no banco")
        
        # Verificar se a tabela foi criada
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'hand_actions'")
        if cursor.fetchone()[0] > 0:
            print("✅ Tabela hand_actions criada com sucesso!")
        else:
            print("❌ Tabela hand_actions não foi criada")
            return False
        
        # Verificar estrutura da tabela
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'hand_actions'
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        print("\n📋 Estrutura da tabela hand_actions:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        # Verificar se a view foi criada
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = 'hand_actions_summary'")
        if cursor.fetchone()[0] > 0:
            print("✅ View hand_actions_summary criada com sucesso!")
        else:
            print("⚠️  View hand_actions_summary não foi criada")
        
        # Verificar índices
        cursor.execute("""
            SELECT i.name AS index_name, c.name AS column_name
            FROM sys.indexes i
            INNER JOIN sys.tables t ON i.object_id = t.object_id
            INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            WHERE t.name = 'hand_actions' AND i.is_primary_key = 0
            ORDER BY i.name, ic.key_ordinal
        """)
        indexes = cursor.fetchall()
        print("\n🔍 Índices criados:")
        for idx in indexes:
            print(f"  - {idx[0]} ({idx[1]})")
        
        conn.close()
        print("\n🎉 Migration executada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migration: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Iniciando migration da tabela hand_actions no SQL Server...")
    success = run_sql_server_migration()
    
    if success:
        print("\n✅ Migration concluída com sucesso!")
        print("📝 A tabela hand_actions está pronta para uso no SQL Server.")
        print("🔗 Agora você pode armazenar ações individuais de cada mão com identificação da street.")
    else:
        print("\n❌ Migration falhou!")
        exit(1) 