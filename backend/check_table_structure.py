#!/usr/bin/env python3
"""
Verificar estrutura das tabelas
"""

import os
import pyodbc
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def connect_to_database():
    """Conecta ao banco de dados Azure SQL"""
    
    try:
        # Obter DATABASE_URL do .env
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL não configurada no arquivo .env")
            return None, None
        
        # Extrair informações da DATABASE_URL
        url_part = database_url.replace('mssql+pyodbc://', '')
        credentials_server = url_part.split('@')[0]
        server_database = url_part.split('@')[1].split('?')[0]
        
        username = credentials_server.split(':')[0]
        password = credentials_server.split(':')[1]
        
        # Decodificar caracteres especiais na senha
        import urllib.parse
        password = urllib.parse.unquote(password)
        
        server = server_database.split('/')[0]
        database = server_database.split('/')[1]
        
        print(f"🔗 Conectando ao banco: {server}/{database}")
        
        # String de conexão
        connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes"
        
        # Conectar
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        
        print("✅ Conectado ao banco de dados com sucesso!")
        return connection, cursor
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None, None

def check_table_structure(cursor, table_name):
    """Verifica a estrutura de uma tabela"""
    
    try:
        print(f"\n📋 ESTRUTURA DA TABELA: {table_name}")
        print("-" * 50)
        
        # Obter colunas
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        
        if not columns:
            print(f"❌ Tabela '{table_name}' não encontrada")
            return
        
        for column in columns:
            col_name, data_type, is_nullable, default_value = column
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f"DEFAULT {default_value}" if default_value else ""
            print(f"   {col_name}: {data_type} {nullable} {default}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total de registros: {count}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela '{table_name}': {e}")

def main():
    """Função principal"""
    
    print("🔍 VERIFICADOR DE ESTRUTURA DE TABELAS")
    print("=" * 60)
    
    # Conectar ao banco
    connection, cursor = connect_to_database()
    if not connection:
        return
    
    try:
        # Verificar tabelas principais
        tables = ['hands', 'tournaments', 'hand_actions', 'players']
        
        for table in tables:
            check_table_structure(cursor, table)
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("🔌 Conexão fechada")

if __name__ == "__main__":
    main() 