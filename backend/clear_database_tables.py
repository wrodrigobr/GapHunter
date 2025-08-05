#!/usr/bin/env python3
"""
Script para limpar tabelas do banco de dados para reimportação
"""

import os
import sys
import pyodbc
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseCleaner:
    """Classe para limpar tabelas do banco de dados"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect_to_database(self):
        """Conecta ao banco de dados Azure SQL"""
        
        try:
            # Obter DATABASE_URL do .env
            database_url = os.getenv('DATABASE_URL')
            
            if not database_url:
                print("❌ DATABASE_URL não configurada no arquivo .env")
                return False
            
            # Extrair informações da DATABASE_URL
            try:
                # Remover prefixo mssql+pyodbc://
                url_part = database_url.replace('mssql+pyodbc://', '')
                
                # Separar credenciais e servidor
                credentials_server = url_part.split('@')[0]
                server_database = url_part.split('@')[1].split('?')[0]
                
                # Extrair username e password
                username = credentials_server.split(':')[0]
                password = credentials_server.split(':')[1]
                
                # Decodificar caracteres especiais na senha
                import urllib.parse
                password = urllib.parse.unquote(password)
                
                # Extrair server e database
                server = server_database.split('/')[0]
                database = server_database.split('/')[1]
                
                print(f"🔗 Conectando ao banco:")
                print(f"   Server: {server}")
                print(f"   Database: {database}")
                print(f"   Username: {username}")
                
            except Exception as e:
                print(f"❌ Erro ao extrair configurações da DATABASE_URL: {e}")
                return False
            
            # String de conexão
            connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes"
            
            # Conectar
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            
            print("✅ Conectado ao banco de dados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            return False
    
    def get_table_info(self):
        """Obtém informações sobre as tabelas relacionadas a hand history"""
        
        try:
            # Verificar se tabelas existem
            tables_query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND TABLE_NAME IN ('hands', 'hand_actions', 'tournaments', 'players')
            ORDER BY TABLE_NAME
            """
            
            self.cursor.execute(tables_query)
            tables = [row[0] for row in self.cursor.fetchall()]
            
            print(f"\n📋 TABELAS ENCONTRADAS:")
            for table in tables:
                # Contar registros
                count_query = f"SELECT COUNT(*) FROM {table}"
                self.cursor.execute(count_query)
                count = self.cursor.fetchone()[0]
                print(f"   - {table}: {count} registros")
            
            return tables
            
        except Exception as e:
            print(f"❌ Erro ao obter informações das tabelas: {e}")
            return []
    
    def clear_table(self, table_name: str, confirm: bool = False):
        """Limpa uma tabela específica"""
        
        try:
            if not confirm:
                # Contar registros antes
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = self.cursor.fetchone()[0]
                
                print(f"⚠️  ATENÇÃO: Você está prestes a deletar {count} registros da tabela '{table_name}'")
                response = input(f"❓ Confirma a limpeza da tabela '{table_name}'? (s/N): ").strip().lower()
                
                if response not in ['s', 'sim', 'y', 'yes']:
                    print(f"❌ Operação cancelada para tabela '{table_name}'")
                    return False
            
            # Limpar tabela
            self.cursor.execute(f"DELETE FROM {table_name}")
            deleted_count = self.cursor.rowcount
            
            # Resetar identity se existir
            try:
                self.cursor.execute(f"DBCC CHECKIDENT ('{table_name}', RESEED, 0)")
                print(f"   🔄 Identity resetado")
            except:
                pass  # Tabela pode não ter identity
            
            print(f"✅ Tabela '{table_name}' limpa: {deleted_count} registros removidos")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao limpar tabela '{table_name}': {e}")
            return False
    
    def clear_all_hand_history_tables(self, confirm: bool = False):
        """Limpa todas as tabelas relacionadas a hand history"""
        
        print("\n🧹 LIMPEZA DE TABELAS DE HAND HISTORY")
        print("=" * 50)
        
        # Lista de tabelas para limpar (em ordem de dependência)
        tables_to_clear = [
            'hand_actions',  # Primeiro (depende de hands)
            'hands',         # Segundo (depende de tournaments e players)
            'tournaments',   # Terceiro
            'players'        # Quarto
        ]
        
        # Verificar tabelas existentes
        existing_tables = self.get_table_info()
        
        if not existing_tables:
            print("❌ Nenhuma tabela encontrada")
            return False
        
        # Limpar apenas tabelas que existem
        tables_to_clear = [table for table in tables_to_clear if table in existing_tables]
        
        if not tables_to_clear:
            print("❌ Nenhuma tabela de hand history encontrada para limpar")
            return False
        
        print(f"\n📋 TABELAS QUE SERÃO LIMPAS:")
        for table in tables_to_clear:
            print(f"   - {table}")
        
        if not confirm:
            print(f"\n⚠️  ATENÇÃO: Esta operação irá remover TODOS os dados de hand history!")
            response = input("❓ Confirma a limpeza completa? (s/N): ").strip().lower()
            
            if response not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada")
                return False
        
        # Limpar tabelas
        success_count = 0
        for table in tables_to_clear:
            if self.clear_table(table, confirm=True):
                success_count += 1
        
        print(f"\n📊 RESUMO:")
        print(f"   ✅ Tabelas limpas com sucesso: {success_count}/{len(tables_to_clear)}")
        
        if success_count == len(tables_to_clear):
            print("🎉 Banco de dados limpo! Pronto para nova importação.")
        else:
            print("⚠️  Algumas tabelas não puderam ser limpas. Verifique os erros acima.")
        
        return success_count == len(tables_to_clear)
    
    def close_connection(self):
        """Fecha a conexão com o banco"""
        
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Conexão fechada")

def main():
    """Função principal"""
    
    print("🧹 LIMPADOR DE BANCO DE DADOS - HAND HISTORY")
    print("=" * 60)
    
    cleaner = DatabaseCleaner()
    
    try:
        # Conectar ao banco
        if not cleaner.connect_to_database():
            return
        
        # Mostrar opções
        print("\n📋 OPÇÕES DISPONÍVEIS:")
        print("1. Ver informações das tabelas")
        print("2. Limpar tabela específica")
        print("3. Limpar todas as tabelas de hand history")
        print("4. Sair")
        
        while True:
            option = input("\n❓ Escolha uma opção (1-4): ").strip()
            
            if option == "1":
                cleaner.get_table_info()
            
            elif option == "2":
                tables = cleaner.get_table_info()
                if tables:
                    table_name = input("📝 Digite o nome da tabela: ").strip()
                    if table_name in tables:
                        cleaner.clear_table(table_name)
                    else:
                        print(f"❌ Tabela '{table_name}' não encontrada")
            
            elif option == "3":
                cleaner.clear_all_hand_history_tables()
                break
            
            elif option == "4":
                print("👋 Saindo...")
                break
            
            else:
                print("❌ Opção inválida")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    finally:
        cleaner.close_connection()

if __name__ == "__main__":
    main() 