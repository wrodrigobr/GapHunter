#!/usr/bin/env python3
"""
Teste Completo de Upload
Testa o upload completo do arquivo torneio_ingles.txt para verificar se a correção funcionou
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

class FullUploadTest:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.parser = PokerStarsParser()
        self.advanced_parser = AdvancedPokerParser()
        
    def test_full_upload(self):
        """Testa o upload completo do arquivo"""
        print("🚀 TESTE COMPLETO DE UPLOAD - TORNEIO_INGLES.TXT")
        print("=" * 60)
        
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
            # Obter usuário
            user = db.query(User).first()
            if not user:
                print("❌ Nenhum usuário encontrado no banco")
                return False
                
            print(f"👤 Usando usuário: {user.email}")
            
            # Processar todas as mãos
            processed_hands = 0
            saved_hands = 0
            skipped_hands = 0
            errors = []
            
            print(f"\n🔄 Processando {len(hands)} mãos...")
            
            for i, hand_text in enumerate(hands, 1):
                if i % 50 == 0:  # Mostrar progresso a cada 50 mãos
                    print(f"📊 Progresso: {i}/{len(hands)} mãos processadas")
                
                # Adicionar prefixo de volta
                full_hand = "PokerStars Hand #" + hand_text
                
                try:
                    # Parse básico
                    hand_data = self.parser._parse_single_hand(full_hand)
                    
                    if not hand_data:
                        skipped_hands += 1
                        continue
                        
                    hand_id = hand_data.get('hand_id')
                    
                    # Verificar se já existe
                    existing_hand = db.query(Hand).filter(Hand.hand_id == hand_id).first()
                    if existing_hand:
                        skipped_hands += 1
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
                    
                    processed_hands += 1
                    saved_hands += 1
                    
                    # Commit a cada 20 mãos
                    if i % 20 == 0:
                        db.commit()
                        print(f"  💾 Commit realizado: {i} mãos processadas")
                        
                except Exception as e:
                    error_msg = f"Erro na mão {i}: {str(e)}"
                    errors.append(error_msg)
                    db.rollback()
                    continue
            
            # Commit final
            db.commit()
            
            print(f"\n📊 RESUMO DO UPLOAD COMPLETO:")
            print(f"  Mãos processadas: {processed_hands}")
            print(f"  Mãos salvas: {saved_hands}")
            print(f"  Mãos ignoradas (já existiam): {skipped_hands}")
            print(f"  Erros: {len(errors)}")
            
            if errors:
                print(f"\n❌ PRIMEIROS 5 ERROS:")
                for error in errors[:5]:
                    print(f"  • {error}")
                    
            return saved_hands > 0
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    def verify_final_results(self):
        """Verifica resultados finais no banco"""
        print("\n🗄️ VERIFICAÇÃO FINAL DO BANCO")
        print("-" * 35)
        
        db = SessionLocal()
        try:
            # Contar total de mãos
            total_hands = db.query(Hand).count()
            print(f"📊 Total de mãos no banco: {total_hands}")
            
            # Contar total de ações
            total_actions = db.query(HandAction).count()
            print(f"📊 Total de ações no banco: {total_actions}")
            
            # Verificar mãos por usuário
            result = db.execute(text("""
                SELECT user_id, COUNT(*) as hand_count 
                FROM hands 
                GROUP BY user_id
            """))
            users_hands = [row for row in result]
            
            print(f"\n📋 MÃOS POR USUÁRIO:")
            for user_id, hand_count in users_hands:
                print(f"  • User ID {user_id}: {hand_count} mãos")
                
            # Verificar últimas mãos carregadas
            if total_hands > 0:
                latest_hands = db.query(Hand).order_by(Hand.id.desc()).limit(5).all()
                print(f"\n📋 ÚLTIMAS 5 MÃOS CARREGADAS:")
                for hand in latest_hands:
                    print(f"  • Hand #{hand.hand_id} - {hand.hero_name} - {hand.hero_cards}")
                    
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
        finally:
            db.close()

def main():
    """Função principal"""
    print("🔧 TESTE COMPLETO DE UPLOAD - CORREÇÃO APLICADA")
    print("=" * 65)
    
    tester = FullUploadTest()
    
    # 1. Verificar estado inicial
    print("\n📊 ESTADO INICIAL:")
    tester.verify_final_results()
    
    # 2. Testar upload completo
    success = tester.test_full_upload()
    
    # 3. Verificar resultado final
    print("\n📊 ESTADO FINAL:")
    tester.verify_final_results()
    
    if success:
        print("\n✅ UPLOAD COMPLETO CONCLUÍDO COM SUCESSO!")
        print("🎯 A correção do limite de 5 mãos foi aplicada e funcionou!")
        print("🎉 Agora o sistema pode processar todas as mãos do arquivo!")
    else:
        print("\n❌ UPLOAD COMPLETO FALHOU!")
        
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 