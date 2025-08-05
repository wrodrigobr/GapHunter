#!/usr/bin/env python3
"""
Script de importação de hand history com tradução automática
- Detecta idioma automaticamente
- Traduz português → inglês durante importação
- Extrai ações estruturadas
- Salva dados prontos para RIROPO
"""

import pyodbc
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from hand_history_translator import HandHistoryTranslator

class HandHistoryImporter:
    """Importador de hand history com tradução automática"""
    
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
    
    def import_hand_history(self, hand_text: str, source_file: str = None) -> dict:
        """Importa hand history com tradução automática"""
        
        print(f"📥 Importando hand history...")
        
        # Detectar idioma e traduzir se necessário
        language = self.translator.detect_language(hand_text)
        
        if language == "portuguese":
            print(f"🌍 Detectado: PORTUGUÊS → Traduzindo para inglês...")
            translated_hand = self.translator.translate_hand_history(hand_text)
            original_language = "portuguese"
        else:
            print(f"🌍 Detectado: INGLÊS → Mantendo formato original")
            translated_hand = hand_text
            original_language = "english"
        
        # Extrair informações básicas
        hand_info = self._extract_hand_info(translated_hand)
        
        # Extrair ações estruturadas
        actions = self._extract_actions_from_hand(translated_hand)
        
        # Salvar no banco
        hand_id = self._save_to_database(hand_info, translated_hand, actions, source_file, original_language)
        
        return {
            'hand_id': hand_id,
            'language': original_language,
            'actions_count': len(actions),
            'translated': language == "portuguese"
        }
    
    def _extract_hand_info(self, hand_text: str) -> dict:
        """Extrai informações básicas do hand history"""
        
        # Padrões para extrair informações
        hand_id_match = re.search(r'PokerStars Hand #(\d+)', hand_text)
        tournament_match = re.search(r'Tournament #(\d+)', hand_text)
        table_match = re.search(r"Table '([^']+)'", hand_text)
        hero_match = re.search(r'Dealt to (\w+)', hand_text)
        
        # Extrair blinds
        blinds_match = re.search(r'Level \w+ \((\d+)/(\d+)\)', hand_text)
        
        # Extrair data
        date_match = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', hand_text)
        
        return {
            'hand_id': hand_id_match.group(1) if hand_id_match else None,
            'tournament_id': tournament_match.group(1) if tournament_match else None,
            'table_name': table_match.group(1) if table_match else None,
            'hero_name': hero_match.group(1) if hero_match else None,
            'small_blind': int(blinds_match.group(1)) if blinds_match else 0,
            'big_blind': int(blinds_match.group(2)) if blinds_match else 0,
            'date_played': date_match.group(1) if date_match else None
        }
    
    def _extract_actions_from_hand(self, hand_text: str) -> list:
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
            (r'^(\w+): calls (\d+(?:\.\d+)?)$', 'call', 2),
            # Bets
            (r'^(\w+): bets (\d+(?:\.\d+)?)$', 'bet', 2),
            # Raises
            (r'^(\w+): raises (\d+(?:\.\d+)?) to (\d+(?:\.\d+)?)$', 'raise', 2),
            # All-in
            (r'^(\w+): all-in (\d+(?:\.\d+)?)$', 'all-in', 2),
            # Posts blinds
            (r'^(\w+): posts small blind (\d+(?:\.\d+)?)$', 'small_blind', 2),
            (r'^(\w+): posts big blind (\d+(?:\.\d+)?)$', 'big_blind', 2),
            (r'^(\w+): posts the ante (\d+(?:\.\d+)?)$', 'ante', 2),
            # Shows
            (r'^(\w+): shows \[([^\]]+)\]', 'show', 0),
            # Wins
            (r'^(\w+): wins (\d+(?:\.\d+)?)$', 'win', 2),
            # Collected
            (r'^(\w+): collected (\d+(?:\.\d+)?) from pot$', 'collected', 2),
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
    
    def _save_to_database(self, hand_info: dict, translated_hand: str, actions: list, source_file: str, original_language: str) -> int:
        """Salva hand history no banco de dados"""
        
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Inserir na tabela hands
            cursor.execute("""
                INSERT INTO hands 
                (hand_id, table_name, hero_name, hero_cards, board_cards, raw_hand, date_played, source_file, original_language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hand_info['hand_id'],
                hand_info['table_name'],
                hand_info['hero_name'],
                None,  # hero_cards será extraído depois
                None,  # board_cards será extraído depois
                translated_hand,
                hand_info['date_played'],
                source_file,
                original_language
            ))
            
            # Obter ID da mão inserida
            hand_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            
            # Inserir ações
            for action in actions:
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
            
            conn.commit()
            conn.close()
            
            print(f"✅ Hand history salva com ID: {hand_id}")
            return hand_id
            
        except Exception as e:
            print(f"❌ Erro ao salvar no banco: {e}")
            if 'conn' in locals():
                conn.close()
            raise
    
    def import_from_file(self, file_path: str) -> dict:
        """Importa hand history de um arquivo"""
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        print(f"📁 Importando de: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            hand_text = f.read()
        
        return self.import_hand_history(hand_text, str(file_path))
    
    def import_from_text(self, hand_text: str) -> dict:
        """Importa hand history de texto"""
        return self.import_hand_history(hand_text)

def main():
    """Função principal para teste"""
    
    print("📥 IMPORTADOR DE HAND HISTORY COM TRADUÇÃO")
    print("=" * 50)
    
    importer = HandHistoryImporter()
    
    # Exemplo de hand history em português
    portuguese_hand = """Mão PokerStars #257045862415: Torneio #3910307458, $ 0.98+$ 0.12 USD Hold'em No Limit - Nível V (40/80) - 2025/07/22 10:10:49 ET
Mesa '3910307458 12' 9-max Lugar #3 é o botão
Lugar 1: jojosetubal (7835 em fichas)
Lugar 2: Kaptahh (8377 em fichas)
Lugar 3: Andrew Willian (1789 em fichas)
Lugar 4: Maks19111979 (2900 em fichas)
Lugar 5: SuKKinho (4058 em fichas)
Lugar 6: petretudor (636 em fichas)
Lugar 7: varen1k322 (2804 em fichas)
Lugar 8: Cyan Diogenes (9040 em fichas)
Lugar 9: phpro (3000 em fichas)
jojosetubal: posts pequeno blind 40
Kaptahh: posts grande blind 80
*** CARTAS DO BURACO ***
Distribuído para phpro [9d Qc]
Andrew Willian: desiste
Maks19111979: desiste
SuKKinho: paga 80
petretudor: desiste
varen1k322: desiste
Cyan Diogenes: desiste
phpro: aumenta 240 para 320
jojosetubal: desiste
Kaptahh: paga 240
SuKKinho: paga 240"""
    
    try:
        result = importer.import_from_text(portuguese_hand)
        print(f"\n✅ Importação concluída!")
        print(f"📊 Resultado: {result}")
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")

if __name__ == "__main__":
    main() 