#!/usr/bin/env python3
"""
Carregar 20 mãos no banco de dados
"""

import os
import sys
import re
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class Load20HandsToDatabase:
    def __init__(self):
        self.file_path = "20_hands_extracted.txt"
        self.results = {
            "hands_loaded": [],
            "database_inserts": [],
            "errors": []
        }
        
    def get_or_create_user(self, session):
        """Obtém ou cria um usuário para as mãos"""
        # Verificar se existe algum usuário
        result = session.execute(text("SELECT id FROM users LIMIT 1"))
        user = result.fetchone()
        
        if user:
            return user[0]
        else:
            # Criar um usuário de teste
            insert_user = text("""
                INSERT INTO users (username, email, full_name, hashed_password, is_active, created_at)
                VALUES (:username, :email, :full_name, :hashed_password, :is_active, :created_at)
            """)
            
            session.execute(insert_user, {
                "username": "test_user",
                "email": "test@gaphunter.com",
                "full_name": "Test User",
                "hashed_password": "test_hash",
                "is_active": True,
                "created_at": datetime.now()
            })
            
            session.commit()
            
            # Obter o ID do usuário criado
            result = session.execute(text("SELECT id FROM users WHERE username = 'test_user'"))
            user = result.fetchone()
            return user[0]
        
    def parse_hand_text(self, hand_text):
        """Parse uma mão de poker"""
        lines = hand_text.split('\n')
        
        hand_data = {
            "hand_id": None,
            "tournament_id": None,
            "table_name": None,
            "date_played": None,
            "hero_name": None,
            "hero_position": None,
            "hero_cards": None,
            "hero_action": None,
            "pot_size": None,
            "bet_amount": None,
            "board_cards": None,
            "raw_hand": hand_text
        }
        
        for line in lines:
            line = line.strip()
            
            # Hand ID
            if line.startswith("PokerStars Hand #"):
                match = re.search(r"PokerStars Hand #(\d+):", line)
                if match:
                    hand_data["hand_id"] = match.group(1)
                    
            # Tournament ID
            elif "Tournament #" in line:
                match = re.search(r"Tournament #(\d+),", line)
                if match:
                    hand_data["tournament_id"] = match.group(1)
                    
            # Table name
            elif "Table '" in line:
                match = re.search(r"Table '(.+?)'", line)
                if match:
                    hand_data["table_name"] = match.group(1)
                    
            # Date played
            elif "Hold'em No Limit" in line:
                # Extrair data da linha de configuração
                date_match = re.search(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})", line)
                if date_match:
                    hand_data["date_played"] = date_match.group(1)
                    
            # Hero cards
            elif "Dealt to" in line:
                match = re.search(r"Dealt to (.+?) \[(.+?)\]", line)
                if match:
                    hand_data["hero_name"] = match.group(1)
                    hand_data["hero_cards"] = match.group(2)
                    
            # Hero position
            elif "posts small blind" in line or "posts big blind" in line:
                if "posts small blind" in line:
                    hand_data["hero_position"] = "SB"
                elif "posts big blind" in line:
                    hand_data["hero_position"] = "BB"
                    
            # Board cards
            elif line.startswith("Board ["):
                match = re.search(r"Board \[(.+?)\]", line)
                if match:
                    hand_data["board_cards"] = match.group(1)
                    
            # Pot size
            elif "Total pot" in line:
                match = re.search(r"Total pot (\d+)", line)
                if match:
                    hand_data["pot_size"] = float(match.group(1))
                    
            # Bet amount
            elif "bets" in line or "raises" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    hand_data["bet_amount"] = float(match.group(1))
                    
        return hand_data
        
    def load_hands_to_database(self):
        """Carrega as mãos no banco de dados"""
        print("🗄️ CARREGANDO MÃOS NO BANCO DE DADOS")
        print("=" * 40)
        
        if not os.path.exists(self.file_path):
            print(f"❌ Arquivo {self.file_path} não encontrado!")
            return False
            
        # Ler mãos do arquivo
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Separar mãos
        hands = content.split("=== MÃO ")[1:]  # Remover primeira parte vazia
        
        print(f"📊 Mãos encontradas no arquivo: {len(hands)}")
        
        # Conectar com banco
        try:
            engine = create_engine("sqlite:///gaphunter.db")
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Obter ou criar usuário
            user_id = self.get_or_create_user(session)
            print(f"👤 Usando usuário ID: {user_id}")
            
            successful_inserts = 0
            
            for i, hand_text in enumerate(hands, 1):
                print(f"\n📋 Processando Mão {i}:")
                
                # Parse da mão
                hand_data = self.parse_hand_text(hand_text)
                
                if not hand_data["hand_id"]:
                    print(f"  ❌ Hand ID não encontrado")
                    continue
                    
                print(f"  🆔 Hand ID: {hand_data['hand_id']}")
                print(f"  👤 Hero: {hand_data['hero_name'] or 'N/A'}")
                print(f"  🃏 Cards: {hand_data['hero_cards'] or 'N/A'}")
                print(f"  📍 Position: {hand_data['hero_position'] or 'N/A'}")
                print(f"  💰 Pot: {hand_data['pot_size'] or 'N/A'}")
                
                # Inserir no banco
                try:
                    insert_query = text("""
                        INSERT INTO hands (
                            user_id, hand_id, tournament_id, table_name, date_played,
                            hero_name, hero_position, hero_cards, hero_action,
                            pot_size, bet_amount, board_cards, raw_hand,
                            created_at
                        ) VALUES (
                            :user_id, :hand_id, :tournament_id, :table_name, :date_played,
                            :hero_name, :hero_position, :hero_cards, :hero_action,
                            :pot_size, :bet_amount, :board_cards, :raw_hand,
                            :created_at
                        )
                    """)
                    
                    session.execute(insert_query, {
                        "user_id": user_id,
                        "hand_id": hand_data["hand_id"],
                        "tournament_id": hand_data["tournament_id"],
                        "table_name": hand_data["table_name"],
                        "date_played": hand_data["date_played"],
                        "hero_name": hand_data["hero_name"],
                        "hero_position": hand_data["hero_position"],
                        "hero_cards": hand_data["hero_cards"],
                        "hero_action": hand_data["hero_action"],
                        "pot_size": hand_data["pot_size"],
                        "bet_amount": hand_data["bet_amount"],
                        "board_cards": hand_data["board_cards"],
                        "raw_hand": hand_data["raw_hand"],
                        "created_at": datetime.now()
                    })
                    
                    session.commit()
                    print(f"  ✅ Inserida com sucesso")
                    successful_inserts += 1
                    
                    self.results["database_inserts"].append({
                        "hand_id": hand_data["hand_id"],
                        "success": True
                    })
                    
                except Exception as e:
                    print(f"  ❌ Erro ao inserir: {e}")
                    session.rollback()
                    
                    self.results["database_inserts"].append({
                        "hand_id": hand_data["hand_id"],
                        "success": False,
                        "error": str(e)
                    })
                    
            session.close()
            
            print(f"\n📊 RESUMO:")
            print(f"  Total de mãos processadas: {len(hands)}")
            print(f"  Inserções bem-sucedidas: {successful_inserts}")
            print(f"  Taxa de sucesso: {(successful_inserts/len(hands))*100:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar com banco: {e}")
            return False
            
    def verify_hands_in_database(self):
        """Verifica se as mãos foram carregadas no banco"""
        print("\n🔍 VERIFICANDO MÃOS NO BANCO DE DADOS")
        print("-" * 40)
        
        try:
            engine = create_engine("sqlite:///gaphunter.db")
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Contar total de mãos
            result = session.execute(text("SELECT COUNT(*) FROM hands"))
            total_hands = result.fetchone()[0]
            print(f"📊 Total de mãos no banco: {total_hands}")
            
            if total_hands > 0:
                print("\n📋 ÚLTIMAS 10 MÃOS CARREGADAS:")
                result = session.execute(text("""
                    SELECT hand_id, hero_name, hero_cards, hero_position, pot_size, created_at 
                    FROM hands 
                    ORDER BY id DESC 
                    LIMIT 10
                """))
                
                hands = [row for row in result]
                for hand in hands:
                    print(f"  • Hand #{hand[0]} - {hand[1]} - {hand[2]} - {hand[3]} - ${hand[4]}")
                    
            session.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
            
    def save_results(self):
        """Salva resultados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_20_hands_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Resultados salvos em: {filename}")
        
    def run_load_test(self):
        """Executa teste de carregamento"""
        print("🚀 INICIANDO CARREGAMENTO DE 20 MÃOS NO BANCO")
        print("=" * 55)
        
        # 1. Carregar mãos no banco
        if not self.load_hands_to_database():
            return False
            
        # 2. Verificar mãos no banco
        self.verify_hands_in_database()
        
        # 3. Salvar resultados
        self.save_results()
        
        print("\n✅ CARREGAMENTO CONCLUÍDO!")
        return True

def main():
    loader = Load20HandsToDatabase()
    success = loader.run_load_test()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Verifique as mãos carregadas no banco")
        print("2. Teste a funcionalidade do frontend com as mãos")
        print("3. Execute o teste de 20 mãos novamente")
    else:
        print("\n❌ Carregamento falhou. Verifique os erros acima.")
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 