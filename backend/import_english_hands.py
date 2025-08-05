#!/usr/bin/env python3
"""
Importador de Hand History - Apenas inglês
"""

import os
import sys
import re
import pyodbc
from pathlib import Path
from dotenv import load_dotenv
from hand_history_validator import HandHistoryValidator

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

def process_english_file(file_path: str, connection, cursor):
    """Processa um arquivo de hand history em inglês"""
    
    validator = HandHistoryValidator()
    
    try:
        print(f"\n📄 Processando: {Path(file_path).name}")
        
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validar formato
        is_valid, language, message = validator.validate_hand_history(content)
        
        if not is_valid:
            print(f"❌ Arquivo inválido: {message}")
            return False
        
        print(f"✅ Arquivo válido em {language}")
        
        # Separar hands individuais
        hands = re.split(r'\n(?=PokerStars Hand #)', content.strip())
        
        print(f"📊 Encontrados {len(hands)} hands")
        
        processed_count = 0
        
        for i, hand_text in enumerate(hands, 1):
            if not hand_text.strip():
                continue
            
            print(f"   Hand {i}/{len(hands)}...", end=" ")
            
            try:
                # Parse básico do hand
                hand_match = re.search(r'PokerStars Hand #(\d+): Tournament #(\d+)', hand_text)
                if not hand_match:
                    print("❌ Parse falhou")
                    continue
                
                hand_id = hand_match.group(1)
                tournament_id = hand_match.group(2)
                
                # Verificar se já existe
                cursor.execute("SELECT id FROM hands WHERE hand_id = ?", hand_id)
                if cursor.fetchone():
                    print("⏭️  Já existe")
                    continue
                
                # Inserir torneio se não existir
                cursor.execute("SELECT id FROM tournaments WHERE tournament_id = ?", tournament_id)
                tournament_db_id = cursor.fetchone()
                
                if not tournament_db_id:
                    # Parse básico do torneio
                    tournament_match = re.search(r'\$([\d.]+)\+\$([\d.]+) USD Hold\'em No Limit - Level (\w+)', hand_text)
                    if tournament_match:
                        buyin = float(tournament_match.group(1))
                        fee = float(tournament_match.group(2))
                        level = tournament_match.group(3)
                        
                        cursor.execute("""
                            INSERT INTO tournaments (tournament_id, buy_in, date_played, user_id)
                            VALUES (?, ?, GETDATE(), 1)
                        """, (tournament_id, buyin))
                        
                        tournament_db_id = cursor.rowcount
                    else:
                        print("❌ Parse torneio falhou")
                        continue
                else:
                    tournament_db_id = tournament_db_id[0]
                
                # Inserir mão
                cursor.execute("""
                    INSERT INTO hands (hand_id, tournament_id, table_name, hero_name, hero_cards, 
                                     board_cards, pot_size, raw_hand, date_played, user_id)
                    VALUES (?, ?, 'Unknown', NULL, NULL, NULL, 0, ?, GETDATE(), 1)
                """, (hand_id, tournament_db_id, hand_text))
                
                connection.commit()
                print("✅ OK")
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Erro: {str(e)[:50]}")
                continue
        
        print(f"📊 Processados: {processed_count} hands")
        return processed_count > 0
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return False

def main():
    """Função principal"""
    
    print("📥 IMPORTADOR DE HAND HISTORY - APENAS INGLÊS")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("❌ Uso: python import_english_hands.py <arquivo>")
        print("📋 Exemplo: python import_english_hands.py torneio_ingles.txt")
        return
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    # Conectar ao banco
    connection, cursor = connect_to_database()
    if not connection:
        return
    
    try:
        # Processar arquivo
        success = process_english_file(file_path, connection, cursor)
        
        if success:
            print("🎉 Importação concluída com sucesso!")
        else:
            print("❌ Importação falhou")
    
    except KeyboardInterrupt:
        print("\n⚠️  Importação interrompida")
    
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