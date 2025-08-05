#!/usr/bin/env python3
"""
Script para processar mãos existentes no banco Azure SQL
- Traduz português → inglês
- Extrai ações estruturadas
- Salva na tabela hand_actions
"""

import pyodbc
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from hand_history_translator import HandHistoryTranslator

class HandHistoryProcessor:
    """Processador de hand history para importação"""
    
    def __init__(self):
        self.translator = HandHistoryTranslator()
        self.connection_string = self._get_connection_string()
    
    def _get_connection_string(self) -> str:
        """Obtém string de conexão do Azure SQL"""
        load_dotenv()
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL não configurada no arquivo .env")
        
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
        
        return f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes"
    
    def extract_actions_from_hand(self, hand_text: str) -> list:
        """Extrai ações estruturadas do hand history"""
        actions = []
        lines = hand_text.split('\n')
        
        current_street = 'preflop'
        action_order = 0
        
        for line in lines:
            line = line.strip()
            
            # Detectar mudança de street
            if '*** HOLE CARDS ***' in line:
                current_street = 'preflop'
                action_order = 0
            elif '*** FLOP ***' in line:
                current_street = 'flop'
                action_order = 0
            elif '*** TURN ***' in line:
                current_street = 'turn'
                action_order = 0
            elif '*** RIVER ***' in line:
                current_street = 'river'
                action_order = 0
            elif '*** SHOWDOWN ***' in line:
                current_street = 'showdown'
                action_order = 0
            
            # Extrair ações
            action = self._parse_action_line(line, current_street, action_order)
            if action:
                actions.append(action)
                action_order += 1
        
        return actions
    
    def _parse_action_line(self, line: str, street: str, order: int) -> dict:
        """Parse uma linha de ação"""
        
        # Padrões de ações
        patterns = [
            # Folds
            (r'^(\w+): folds$', 'fold', 0),
            # Checks
            (r'^(\w+): checks$', 'check', 0),
            # Calls
            (r'^(\w+): calls \$(\d+(?:\.\d+)?)$', 'call', 2),
            # Bets
            (r'^(\w+): bets \$(\d+(?:\.\d+)?)$', 'bet', 2),
            # Raises
            (r'^(\w+): raises \$(\d+(?:\.\d+)?) to \$(\d+(?:\.\d+)?)$', 'raise', 2),
            # All-in
            (r'^(\w+): all-in \$(\d+(?:\.\d+)?)$', 'all-in', 2),
            # Posts blinds
            (r'^(\w+): posts small blind \$(\d+(?:\.\d+)?)$', 'small_blind', 2),
            (r'^(\w+): posts big blind \$(\d+(?:\.\d+)?)$', 'big_blind', 2),
            # Shows
            (r'^(\w+): shows \[([^\]]+)\]', 'show', 0),
            # Wins
            (r'^(\w+): wins \$(\d+(?:\.\d+)?)$', 'win', 2),
            # Collected
            (r'^(\w+): collected \$(\d+(?:\.\d+)?)$', 'collected', 2),
        ]
        
        for pattern, action_type, amount_group in patterns:
            match = re.match(pattern, line)
            if match:
                player_name = match.group(1)
                amount = float(match.group(amount_group)) if amount_group > 0 else 0
                total_bet = amount
                
                # Para raises, o total_bet é o terceiro grupo
                if action_type == 'raise' and len(match.groups()) >= 3:
                    total_bet = float(match.group(3))
                
                return {
                    'street': street,
                    'player_name': player_name,
                    'action_type': action_type,
                    'amount': amount,
                    'total_bet': total_bet,
                    'action_order': order
                }
        
        return None
    
    def process_existing_hands(self, limit: int = 10):
        """Processa mãos existentes no banco"""
        
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            print(f"🔗 Conectado ao Azure SQL")
            
            # Buscar mãos não processadas
            cursor.execute(f"""
                SELECT TOP {limit} 
                    id, hand_id, raw_hand, table_name, hero_name
                FROM hands 
                WHERE raw_hand IS NOT NULL
                ORDER BY id
            """)
            
            hands = cursor.fetchall()
            print(f"📊 Encontradas {len(hands)} mãos para processar")
            
            processed_count = 0
            translated_count = 0
            
            for hand in hands:
                hand_id, pokerstars_hand_id, raw_hand, table_name, hero_name = hand
                
                print(f"\n🔄 Processando mão {pokerstars_hand_id}...")
                
                # Detectar idioma e traduzir se necessário
                language = self.translator.detect_language(raw_hand)
                
                if language == "portuguese":
                    print(f"🌍 Traduzindo de português para inglês...")
                    translated_hand = self.translator.translate_hand_history(raw_hand)
                    translated_count += 1
                else:
                    translated_hand = raw_hand
                
                # Extrair ações
                actions = self.extract_actions_from_hand(translated_hand)
                print(f"🎯 Extraídas {len(actions)} ações")
                
                # Salvar ações na tabela hand_actions
                for action in actions:
                    try:
                        cursor.execute("""
                            INSERT INTO hand_actions 
                            (hand_id, street, player_name, action_type, amount, total_bet, action_order)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            hand_id,
                            action['street'],
                            action['player_name'],
                            action['action_type'],
                            action['amount'],
                            action['total_bet'],
                            action['action_order']
                        ))
                    except pyodbc.Error as e:
                        if "duplicate" not in str(e).lower():
                            print(f"⚠️  Erro ao salvar ação: {e}")
                
                # Atualizar raw_hand com versão traduzida (se necessário)
                if language == "portuguese":
                    cursor.execute("""
                        UPDATE hands 
                        SET raw_hand = ? 
                        WHERE id = ?
                    """, (translated_hand, hand_id))
                
                processed_count += 1
                
                # Commit a cada 5 mãos
                if processed_count % 5 == 0:
                    conn.commit()
                    print(f"💾 Commit realizado - {processed_count} mãos processadas")
            
            # Commit final
            conn.commit()
            
            print(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
            print(f"📊 Total processado: {processed_count} mãos")
            print(f"🌍 Traduzidas: {translated_count} mãos")
            
            # Verificar resultados
            cursor.execute("SELECT COUNT(*) FROM hand_actions")
            total_actions = cursor.fetchone()[0]
            print(f"🎯 Total de ações estruturadas: {total_actions}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro durante processamento: {e}")
            if 'conn' in locals():
                conn.close()
    
    def create_hand_actions_table_if_not_exists(self):
        """Cria a tabela hand_actions se não existir"""
        
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'hand_actions'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("📋 Criando tabela hand_actions...")
                
                # Criar tabela
                cursor.execute("""
                    CREATE TABLE hand_actions (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        hand_id INT NOT NULL,
                        street VARCHAR(20) NOT NULL,
                        player_name VARCHAR(50) NOT NULL,
                        action_type VARCHAR(20) NOT NULL,
                        amount DECIMAL(10,2) DEFAULT 0.00,
                        total_bet DECIMAL(10,2) DEFAULT 0.00,
                        action_order INT NOT NULL,
                        created_at DATETIME2 DEFAULT GETDATE(),
                        FOREIGN KEY (hand_id) REFERENCES hands(id) ON DELETE CASCADE
                    )
                """)
                
                # Criar índices
                cursor.execute("CREATE INDEX idx_hand_actions_hand_id ON hand_actions(hand_id)")
                cursor.execute("CREATE INDEX idx_hand_actions_street ON hand_actions(street)")
                cursor.execute("CREATE INDEX idx_hand_actions_player ON hand_actions(player_name)")
                cursor.execute("CREATE INDEX idx_hand_actions_type ON hand_actions(action_type)")
                cursor.execute("CREATE INDEX idx_hand_actions_order ON hand_actions(action_order)")
                
                conn.commit()
                print("✅ Tabela hand_actions criada com sucesso!")
            else:
                print("✅ Tabela hand_actions já existe")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            if 'conn' in locals():
                conn.close()

def main():
    """Função principal"""
    
    print("🔄 PROCESSAMENTO DE MÃOS EXISTENTES")
    print("=" * 50)
    
    processor = HandHistoryProcessor()
    
    # Criar tabela se necessário
    processor.create_hand_actions_table_if_not_exists()
    
    # Processar mãos (limite de 10 para teste)
    processor.process_existing_hands(limit=10)
    
    print("\n🎉 Processamento concluído!")

if __name__ == "__main__":
    main() 