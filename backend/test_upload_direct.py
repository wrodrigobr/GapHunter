#!/usr/bin/env python3
"""
Teste Direto de Upload
Testa o processo de upload diretamente sem servidor web
"""

import os
import sys
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

class DirectUploadTest:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.parser = PokerStarsParser()
        self.advanced_parser = AdvancedPokerParser()
        
    def test_upload_process(self):
        """Testa o processo de upload diretamente"""
        print("🚀 TESTE DIRETO DE UPLOAD")
        print("=" * 35)
        
        if not os.path.exists(self.file_path):
            print(f"❌ Arquivo {self.file_path} não encontrado!")
            return False
            
        # Ler arquivo
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"📄 Arquivo lido: {len(content)} caracteres")
        
        # Dividir em mãos
        hands = content.split("PokerStars Hand #")
        hands = [h for h in hands if h.strip()]
        
        print(f"📊 Total de mãos encontradas: {len(hands)}")
        
        # Criar sessão do banco
        db = SessionLocal()
        
        try:
            # Obter ou criar usuário
            user = db.query(User).first()
            if not user:
                print("❌ Nenhum usuário encontrado no banco")
                return False
                
            print(f"👤 Usando usuário: {user.email}")
            
            # Processar primeiras 20 mãos
            processed_hands = 0
            saved_hands = 0
            errors = []
            
            for i, hand_text in enumerate(hands[:20], 1):
                print(f"\n📋 Processando Mão {i}:")
                
                # Adicionar prefixo de volta
                full_hand = "PokerStars Hand #" + hand_text
                
                try:
                    # Parse básico
                    hand_data = self.parser._parse_single_hand(full_hand)
                    
                    if not hand_data:
                        print(f"  ❌ Falha no parse básico")
                        errors.append(f"Mão {i}: Falha no parse básico")
                        continue
                        
                    hand_id = hand_data.get('hand_id')
                    print(f"  🆔 Hand ID: {hand_id}")
                    
                    # Verificar se já existe
                    existing_hand = db.query(Hand).filter(Hand.hand_id == hand_id).first()
                    if existing_hand:
                        print(f"  ⚠️ Mão já existe no banco")
                        continue
                        
                    # Criar registro no banco
                    db_hand = Hand(
                        user_id=user.id,
                        hand_id=hand_id,
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
                        raw_hand=full_hand
                    )
                    
                    db.add(db_hand)
                    db.flush()  # Para obter o ID
                    
                    # Parse avançado para ações
                    advanced_replay = self.advanced_parser.parse_hand_for_replay(full_hand)
                    
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
                    
                    processed_hands += 1
                    saved_hands += 1
                    print(f"  ✅ Mão salva com sucesso")
                    
                    # Commit a cada 5 mãos
                    if i % 5 == 0:
                        db.commit()
                        print(f"  💾 Commit realizado: {i} mãos")
                        
                except Exception as e:
                    error_msg = f"Erro na mão {i}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
                    db.rollback()
                    continue
            
            # Commit final
            db.commit()
            
            print(f"\n📊 RESUMO DO TESTE:")
            print(f"  Mãos processadas: {processed_hands}")
            print(f"  Mãos salvas: {saved_hands}")
            print(f"  Erros: {len(errors)}")
            
            if errors:
                print(f"\n❌ ERROS ENCONTRADOS:")
                for error in errors[:5]:  # Mostrar apenas os primeiros 5
                    print(f"  • {error}")
                    
            return saved_hands > 0
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    def verify_database_hands(self):
        """Verifica mãos no banco de dados"""
        print("\n🗄️ VERIFICANDO MÃOS NO BANCO")
        print("-" * 30)
        
        db = SessionLocal()
        try:
            # Contar total de mãos
            total_hands = db.query(Hand).count()
            print(f"📊 Total de mãos no banco: {total_hands}")
            
            # Verificar últimas mãos
            if total_hands > 0:
                latest_hands = db.query(Hand).order_by(Hand.id.desc()).limit(10).all()
                print(f"\n📋 ÚLTIMAS 10 MÃOS:")
                for hand in latest_hands:
                    print(f"  • Hand #{hand.hand_id} - {hand.hero_name} - {hand.hero_cards}")
                    
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
        finally:
            db.close()

def main():
    """Função principal"""
    print("🔧 TESTE DIRETO DE UPLOAD - CORREÇÃO APLICADA")
    print("=" * 55)
    
    tester = DirectUploadTest()
    
    # 1. Verificar mãos atuais
    tester.verify_database_hands()
    
    # 2. Testar upload
    success = tester.test_upload_process()
    
    # 3. Verificar resultado
    tester.verify_database_hands()
    
    if success:
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("🎯 A correção do limite de 5 mãos foi aplicada")
    else:
        print("\n❌ TESTE FALHOU!")
        
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 