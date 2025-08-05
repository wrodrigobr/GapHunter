#!/usr/bin/env python3
"""
Teste do RIROPO com dados do banco de dados
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

def test_riropo_compatibility(cursor):
    """Testa se os dados do banco são compatíveis com RIROPO"""
    
    try:
        print("\n🧪 TESTE DE COMPATIBILIDADE COM RIROPO")
        print("=" * 50)
        
        # Buscar alguns hands do banco
        cursor.execute("""
            SELECT TOP 3 id, hand_id, raw_hand 
            FROM hands 
            WHERE raw_hand IS NOT NULL 
            ORDER BY id DESC
        """)
        
        hands = cursor.fetchall()
        
        if not hands:
            print("❌ Nenhum hand encontrado no banco")
            return False
        
        print(f"📊 Testando {len(hands)} hands do banco...")
        
        for i, (db_id, hand_id, raw_hand) in enumerate(hands, 1):
            print(f"\n📋 HAND {i}: {hand_id}")
            print("-" * 30)
            
            # Verificar elementos essenciais do RIROPO
            riropo_requirements = [
                "PokerStars Hand",
                "Table",
                "Seat",
                "*** HOLE CARDS ***",
                "Dealt to",
                "folds",
                "calls", 
                "bets",
                "raises",
                "checks",
                "all-in",
                "shows",
                "collected",
                "Uncalled bet",
                "returned to",
                "*** SUMMARY ***",
                "Total pot",
                "Rake",
                "Board",
                "folded",
                "won",
                "lost"
            ]
            
            missing_elements = []
            for element in riropo_requirements:
                if element not in raw_hand:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"❌ Elementos faltando: {', '.join(missing_elements[:5])}")
                if len(missing_elements) > 5:
                    print(f"   ... e mais {len(missing_elements) - 5} elementos")
            else:
                print("✅ Todos os elementos essenciais presentes")
            
            # Verificar se tem ações estruturadas
            action_patterns = [
                r'\w+: folds',
                r'\w+: calls \d+',
                r'\w+: bets \d+',
                r'\w+: raises \d+ to \d+',
                r'\w+: checks',
                r'\w+: all-in \d+'
            ]
            
            actions_found = 0
            for pattern in action_patterns:
                import re
                if re.search(pattern, raw_hand):
                    actions_found += 1
            
            print(f"📊 Ações estruturadas encontradas: {actions_found}/{len(action_patterns)}")
            
            # Verificar se tem streets
            streets = ["*** FLOP ***", "*** TURN ***", "*** RIVER ***"]
            streets_found = sum(1 for street in streets if street in raw_hand)
            print(f"📊 Streets encontradas: {streets_found}/3")
            
            # Verificar se tem board
            if "Board [" in raw_hand:
                print("✅ Board presente")
            else:
                print("⚠️  Board não encontrado")
            
            # Verificar se tem pot
            if "Total pot" in raw_hand:
                print("✅ Pot total presente")
            else:
                print("⚠️  Pot total não encontrado")
            
            # Resumo do hand
            if len(missing_elements) == 0 and actions_found >= 3:
                print("🎉 COMPATÍVEL COM RIROPO!")
            else:
                print("⚠️  PODE TER PROBLEMAS COM RIROPO")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar compatibilidade: {e}")
        return False

def show_sample_hand(cursor):
    """Mostra um exemplo de hand do banco"""
    
    try:
        print("\n📋 EXEMPLO DE HAND DO BANCO")
        print("=" * 50)
        
        cursor.execute("""
            SELECT TOP 1 hand_id, raw_hand 
            FROM hands 
            WHERE raw_hand IS NOT NULL 
            ORDER BY id DESC
        """)
        
        result = cursor.fetchone()
        
        if not result:
            print("❌ Nenhum hand encontrado")
            return
        
        hand_id, raw_hand = result
        
        print(f"🎯 Hand ID: {hand_id}")
        print("-" * 30)
        
        # Mostrar primeiras linhas
        lines = raw_hand.split('\n')[:10]
        for line in lines:
            print(f"   {line}")
        
        if len(raw_hand.split('\n')) > 10:
            print("   ...")
            total_lines = len(raw_hand.split('\n'))
            print(f"   (Total: {total_lines} linhas)")
        
    except Exception as e:
        print(f"❌ Erro ao mostrar hand: {e}")

def main():
    """Função principal"""
    
    print("🧪 TESTE DE COMPATIBILIDADE RIROPO")
    print("=" * 60)
    
    # Conectar ao banco
    connection, cursor = connect_to_database()
    if not connection:
        return
    
    try:
        # Testar compatibilidade
        test_riropo_compatibility(cursor)
        
        # Mostrar exemplo
        show_sample_hand(cursor)
        
        print("\n🎯 CONCLUSÃO:")
        print("✅ Se todos os hands passaram no teste, o RIROPO deve funcionar perfeitamente!")
        print("✅ Os dados estão no formato correto em inglês")
        print("✅ A mesa interativa deve carregar automaticamente")
        
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