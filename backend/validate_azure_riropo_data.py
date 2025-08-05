#!/usr/bin/env python3
"""
Script para validar se os dados do Azure SQL estão compatíveis com o RIROPO
"""

import pyodbc
import os
from pathlib import Path
from dotenv import load_dotenv

def validate_azure_riropo_compatibility():
    """Valida se os dados do Azure SQL estão compatíveis com o RIROPO"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações do banco Azure SQL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não configurada no arquivo .env")
        return False
    
    # Extrair informações da DATABASE_URL
    # Formato: mssql+pyodbc://username:password@server/database?driver=...
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
        
        print(f"🔗 Configurações extraídas:")
        print(f"   Server: {server}")
        print(f"   Database: {database}")
        print(f"   Username: {username}")
        
    except Exception as e:
        print(f"❌ Erro ao extrair configurações da DATABASE_URL: {e}")
        return False
    
    # String de conexão
    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes"
    
    try:
        # Conectar ao Azure SQL
        print(f"🔗 Conectando ao Azure SQL: {server}/{database}")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print(f"✅ Conectado com sucesso!")
        
        # 1. Verificar se há dados na tabela hands
        cursor.execute("SELECT COUNT(*) FROM hands")
        total_hands = cursor.fetchone()[0]
        print(f"📊 Total de mãos no banco: {total_hands}")
        
        if total_hands == 0:
            print("⚠️  Nenhuma mão encontrada no banco")
            return False
        
        # 2. Verificar estrutura dos dados
        cursor.execute("""
            SELECT TOP 3
                hand_id,
                table_name,
                hero_name,
                hero_cards,
                board_cards,
                raw_hand,
                date_played
            FROM hands 
        """)
        
        sample_hands = cursor.fetchall()
        
        print("\n📋 Amostra dos dados:")
        for i, hand in enumerate(sample_hands, 1):
            print(f"\n--- Mão {i} ---")
            print(f"Hand ID: {hand[0]}")
            print(f"Table: {hand[1]}")
            print(f"Hero: {hand[2]}")
            print(f"Hero Cards: {hand[3]}")
            print(f"Board: {hand[4]}")
            print(f"Date: {hand[6]}")
            if hand[5]:
                print(f"Raw Hand (primeiros 200 chars): {hand[5][:200]}...")
            else:
                print("Raw Hand: NULL")
        
        # 3. Verificar formato do raw_hand
        print("\n🔍 Validando formato do raw_hand...")
        
        cursor.execute("SELECT TOP 1 raw_hand FROM hands WHERE raw_hand IS NOT NULL")
        result = cursor.fetchone()
        
        if not result or not result[0]:
            print("❌ Nenhum raw_hand válido encontrado")
            return False
        
        raw_hand = result[0]
        
        # Verificar se contém elementos essenciais do PokerStars
        required_elements = [
            "PokerStars Hand #",
            "Hold'em No Limit",
            "Table '",
            "Seat #",
            "is the button",
            "posts small blind",
            "posts big blind",
            "*** HOLE CARDS ***",
            "Dealt to"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in raw_hand:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Elementos faltando no raw_hand: {missing_elements}")
            print("⚠️  O formato pode não ser compatível com RIROPO")
        else:
            print("✅ Formato do raw_hand parece compatível")
        
        # 4. Verificar idioma
        print("\n🌍 Verificando idioma...")
        
        portuguese_indicators = [
            "pequeno blind",
            "grande blind",
            "cartas do buraco",
            "flop",
            "turno",
            "rio",
            "desiste",
            "paga",
            "aposta",
            "aumenta",
            "all-in"
        ]
        
        english_indicators = [
            "small blind",
            "big blind",
            "hole cards",
            "flop",
            "turn",
            "river",
            "folds",
            "calls",
            "bets",
            "raises",
            "all-in"
        ]
        
        portuguese_count = sum(1 for indicator in portuguese_indicators if indicator in raw_hand)
        english_count = sum(1 for indicator in english_indicators if indicator in raw_hand)
        
        print(f"Indicadores em português: {portuguese_count}")
        print(f"Indicadores em inglês: {english_count}")
        
        if portuguese_count > english_count:
            print("⚠️  Dados parecem estar em português - RIROPO espera inglês")
            needs_translation = True
        else:
            print("✅ Dados parecem estar em inglês - compatível com RIROPO")
            needs_translation = False
        
        # 5. Verificar estrutura de ações
        print("\n🎯 Verificando estrutura de ações...")
        
        # Verificar se há ações estruturadas
        cursor.execute("SELECT COUNT(*) FROM hand_actions")
        total_actions = cursor.fetchone()[0]
        
        if total_actions > 0:
            print(f"✅ {total_actions} ações estruturadas encontradas")
            
            # Verificar amostra de ações
            cursor.execute("""
                SELECT TOP 5 street, player_name, action_type, amount, action_order
                FROM hand_actions 
                ORDER BY hand_id, street, action_order 
            """)
            
            sample_actions = cursor.fetchall()
            print("📋 Amostra de ações:")
            for action in sample_actions:
                print(f"  {action[0]}: {action[1]} {action[2]} ${action[3]} (ordem: {action[4]})")
        else:
            print("⚠️  Nenhuma ação estruturada encontrada")
            print("💡 Será necessário processar o raw_hand para extrair ações")
        
        conn.close()
        
        # 6. Recomendações
        print("\n📝 RECOMENDAÇÕES:")
        
        if needs_translation:
            print("🔄 1. Converter dados para inglês antes de usar com RIROPO")
        
        if total_actions == 0:
            print("🔄 2. Processar raw_hand para extrair ações estruturadas")
        
        print("🔄 3. Testar com uma mão específica no RIROPO")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        return False

def test_riropo_parser_with_azure_sample():
    """Testa o parser RIROPO com uma amostra do Azure SQL"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações do banco Azure SQL
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
        
    except Exception as e:
        print(f"❌ Erro ao extrair configurações da DATABASE_URL: {e}")
        return False
    
    # String de conexão
    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes"
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Pegar uma mão completa
        cursor.execute("""
            SELECT TOP 1 raw_hand, hand_id, table_name
            FROM hands 
            WHERE raw_hand IS NOT NULL 
            AND LEN(raw_hand) > 100
        """)
        
        result = cursor.fetchone()
        if not result:
            print("❌ Nenhuma mão válida encontrada para teste")
            return False
        
        raw_hand, hand_id, table_name = result
        
        print(f"\n🧪 Testando parser RIROPO com mão {hand_id}...")
        print(f"Table: {table_name}")
        print(f"Raw hand length: {len(raw_hand)} caracteres")
        
        # Salvar em arquivo temporário para teste
        test_file = Path(__file__).parent / "test_hand.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(raw_hand)
        
        print(f"📄 Mão salva em: {test_file}")
        print("💡 Você pode testar esta mão diretamente no RIROPO")
        
        # Mostrar primeiras linhas
        lines = raw_hand.split('\n')[:10]
        print("\n📋 Primeiras linhas da mão:")
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VALIDAÇÃO DE COMPATIBILIDADE RIROPO - AZURE SQL")
    print("=" * 60)
    
    success = validate_azure_riropo_compatibility()
    
    if success:
        print("\n🧪 TESTE DO PARSER")
        print("=" * 30)
        test_riropo_parser_with_azure_sample()
    
    print("\n✅ Validação concluída!") 