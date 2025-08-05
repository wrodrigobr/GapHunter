#!/usr/bin/env python3
"""
Análise de Mãos Faltantes
Identifica quais mãos não foram carregadas e por quê
"""

import os
import sys
import re
from pathlib import Path

# Adicionar o diretório raiz ao path
backend_root = Path(__file__).parent
sys.path.append(str(backend_root))

from app.models.database import SessionLocal, engine
from app.models.hand import Hand
from app.models.hand_action import HandAction
from app.models.user import User
from app.utils.poker_parser import PokerStarsParser
from app.utils.advanced_poker_parser import AdvancedPokerParser
from sqlalchemy import text

class MissingHandsAnalyzer:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.parser = PokerStarsParser()
        self.advanced_parser = AdvancedPokerParser()
        
    def extract_all_hand_ids_from_file(self):
        """Extrai todos os hand IDs do arquivo"""
        print("📄 EXTRAINDO TODOS OS HAND IDs DO ARQUIVO")
        print("=" * 50)
        
        if not os.path.exists(self.file_path):
            print(f"❌ Arquivo {self.file_path} não encontrado!")
            return []
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Encontrar todos os hand IDs
        hand_matches = re.findall(r"PokerStars Hand #(\d+):", content)
        hand_ids = [int(hand_id) for hand_id in hand_matches]
        
        print(f"📊 Total de hand IDs encontrados no arquivo: {len(hand_ids)}")
        print(f"📋 Primeiros 10: {hand_ids[:10]}")
        print(f"📋 Últimos 10: {hand_ids[-10:]}")
        
        return hand_ids
        
    def get_loaded_hand_ids_from_database(self):
        """Obtém todos os hand IDs carregados no banco"""
        print("\n🗄️ OBTENDO HAND IDs DO BANCO DE DADOS")
        print("-" * 45)
        
        db = SessionLocal()
        try:
            hands = db.query(Hand.hand_id).all()
            loaded_hand_ids = [int(hand[0]) for hand in hands]
            
            print(f"📊 Total de hand IDs no banco: {len(loaded_hand_ids)}")
            print(f"📋 Primeiros 10: {loaded_hand_ids[:10]}")
            print(f"📋 Últimos 10: {loaded_hand_ids[-10:]}")
            
            return loaded_hand_ids
        except Exception as e:
            print(f"❌ Erro ao obter hand IDs do banco: {e}")
            return []
        finally:
            db.close()
            
    def find_missing_hand_ids(self, file_hand_ids, db_hand_ids):
        """Encontra hand IDs que estão no arquivo mas não no banco"""
        print("\n🔍 IDENTIFICANDO HAND IDs FALTANTES")
        print("-" * 40)
        
        file_set = set(file_hand_ids)
        db_set = set(db_hand_ids)
        
        missing_hand_ids = file_set - db_set
        
        print(f"📊 Hand IDs no arquivo: {len(file_set)}")
        print(f"📊 Hand IDs no banco: {len(db_set)}")
        print(f"📊 Hand IDs faltantes: {len(missing_hand_ids)}")
        
        if missing_hand_ids:
            missing_list = sorted(list(missing_hand_ids))
            print(f"📋 Hand IDs faltantes: {missing_list}")
            
        return missing_hand_ids
        
    def analyze_missing_hands(self, missing_hand_ids):
        """Analisa as mãos faltantes para identificar o problema"""
        print("\n🔍 ANALISANDO MÃOS FALTANTES")
        print("-" * 35)
        
        if not missing_hand_ids:
            print("✅ Nenhuma mão faltante encontrada!")
            return
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for hand_id in sorted(missing_hand_ids):
            print(f"\n📋 Analisando Hand ID: {hand_id}")
            
            # Encontrar a mão no arquivo
            hand_pattern = f"PokerStars Hand #{hand_id}:"
            hand_start = content.find(hand_pattern)
            
            if hand_start == -1:
                print(f"  ❌ Hand ID {hand_id} não encontrado no arquivo!")
                continue
                
            # Extrair a mão completa
            hand_end = content.find("PokerStars Hand #", hand_start + 1)
            if hand_end == -1:
                hand_end = len(content)
                
            hand_text = content[hand_start:hand_end].strip()
            
            print(f"  📄 Tamanho da mão: {len(hand_text)} caracteres")
            
            # Tentar parse básico
            try:
                hand_data = self.parser._parse_single_hand(hand_text)
                if hand_data:
                    print(f"  ✅ Parse básico OK - Hand ID: {hand_data.get('hand_id')}")
                    print(f"  📊 Hero: {hand_data.get('hero_name')} - Cards: {hand_data.get('hero_cards')}")
                    
                    # Verificar se tem ações
                    action_count = len(re.findall(r"(\w+): (folds|calls|raises|bets|checks|all-in)", hand_text))
                    print(f"  🎯 Ações encontradas: {action_count}")
                    
                    # Tentar parse avançado
                    advanced_replay = self.advanced_parser.parse_hand_for_replay(hand_text)
                    if advanced_replay:
                        total_actions = sum(len(street.actions) for street in advanced_replay.streets)
                        print(f"  ✅ Parse avançado OK - {total_actions} ações")
                    else:
                        print(f"  ❌ Parse avançado falhou")
                        
                else:
                    print(f"  ❌ Parse básico falhou")
                    
            except Exception as e:
                print(f"  ❌ Erro no parse: {e}")
                
            # Mostrar primeiras linhas da mão
            lines = hand_text.split('\n')[:5]
            print(f"  📄 Primeiras linhas:")
            for line in lines:
                print(f"    {line}")
                
    def test_loading_missing_hands(self, missing_hand_ids):
        """Testa carregar as mãos faltantes"""
        print("\n🧪 TESTANDO CARREGAMENTO DAS MÃOS FALTANTES")
        print("-" * 50)
        
        if not missing_hand_ids:
            print("✅ Nenhuma mão faltante para testar!")
            return
            
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                print("❌ Nenhum usuário encontrado no banco")
                return
                
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            success_count = 0
            error_count = 0
            
            for hand_id in sorted(missing_hand_ids):
                print(f"\n📋 Testando Hand ID: {hand_id}")
                
                # Encontrar a mão no arquivo
                hand_pattern = f"PokerStars Hand #{hand_id}:"
                hand_start = content.find(hand_pattern)
                
                if hand_start == -1:
                    print(f"  ❌ Hand ID {hand_id} não encontrado no arquivo!")
                    error_count += 1
                    continue
                    
                # Extrair a mão completa
                hand_end = content.find("PokerStars Hand #", hand_start + 1)
                if hand_end == -1:
                    hand_end = len(content)
                    
                hand_text = content[hand_start:hand_end].strip()
                
                try:
                    # Parse básico
                    hand_data = self.parser._parse_single_hand(hand_text)
                    
                    if not hand_data:
                        print(f"  ❌ Parse básico falhou")
                        error_count += 1
                        continue
                        
                    # Verificar se já existe
                    existing_hand = db.query(Hand).filter(Hand.hand_id == str(hand_id)).first()
                    if existing_hand:
                        print(f"  ⚠️ Mão já existe no banco")
                        continue
                        
                    # Criar registro no banco
                    db_hand = Hand(
                        user_id=user.id,
                        hand_id=str(hand_id),
                        pokerstars_tournament_id=hand_data.get('tournament_id'),
                        table_name=hand_data.get('table_name'),
                        date_played=hand_data.get('date_played'),
                        hero_name=hand_data.get('hero_name'),
                        hero_position=hand_data.get('hero_position'),
                        hero_cards=hand_data.get('hero_cards'),
                        hero_action=hand_data.get('hero_action'),
                        pot_size=hand_data.get('pot_size'),
                        bet_amount=hand_data.get('bet_amount'),
                        board_cards=hand_data.get('board_cards'),
                        raw_hand=hand_text
                    )
                    
                    db.add(db_hand)
                    db.flush()
                    
                    # Parse avançado para ações
                    advanced_replay = self.advanced_parser.parse_hand_for_replay(hand_text)
                    
                    if advanced_replay:
                        action_order = 0
                        for street in advanced_replay.streets:
                            for action in street.actions:
                                db_action = HandAction(
                                    hand_id=db_hand.id,
                                    street=action.street,
                                    player_name=action.player,
                                    action_type=action.action_type,
                                    amount=action.amount or 0.0,
                                    total_bet=action.total_bet or 0.0,
                                    action_order=action_order
                                )
                                db.add(db_action)
                                action_order += 1
                        
                        print(f"  ✅ {action_order} ações salvas")
                    
                    success_count += 1
                    print(f"  ✅ Mão carregada com sucesso")
                    
                except Exception as e:
                    print(f"  ❌ Erro ao carregar mão: {e}")
                    error_count += 1
                    db.rollback()
                    continue
                    
            # Commit final
            db.commit()
            
            print(f"\n📊 RESUMO DO TESTE:")
            print(f"  Mãos carregadas com sucesso: {success_count}")
            print(f"  Mãos com erro: {error_count}")
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            db.rollback()
        finally:
            db.close()

def main():
    """Função principal"""
    print("🔍 ANÁLISE DE MÃOS FALTANTES - TORNEIO_INGLES.TXT")
    print("=" * 60)
    
    analyzer = MissingHandsAnalyzer()
    
    # 1. Extrair hand IDs do arquivo
    file_hand_ids = analyzer.extract_all_hand_ids_from_file()
    
    # 2. Obter hand IDs do banco
    db_hand_ids = analyzer.get_loaded_hand_ids_from_database()
    
    # 3. Encontrar hand IDs faltantes
    missing_hand_ids = analyzer.find_missing_hand_ids(file_hand_ids, db_hand_ids)
    
    # 4. Analisar mãos faltantes
    analyzer.analyze_missing_hands(missing_hand_ids)
    
    # 5. Testar carregamento das mãos faltantes
    analyzer.test_loading_missing_hands(missing_hand_ids)
    
    # 6. Verificar resultado final
    print("\n📊 VERIFICAÇÃO FINAL:")
    final_db_hand_ids = analyzer.get_loaded_hand_ids_from_database()
    final_missing = analyzer.find_missing_hand_ids(file_hand_ids, final_db_hand_ids)
    
    if not final_missing:
        print("✅ TODAS AS MÃOS FORAM CARREGADAS COM SUCESSO!")
    else:
        print(f"❌ Ainda faltam {len(final_missing)} mãos: {sorted(list(final_missing))}")
        
    return len(final_missing) == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 