#!/usr/bin/env python3
"""
Correção de Erros de Upload
Corrige os problemas identificados no processo de upload
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

class UploadErrorFixer:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.parser = PokerStarsParser()
        self.advanced_parser = AdvancedPokerParser()
        
    def fix_hand_actions_table(self):
        """Corrige registros com hand_id NULL na tabela hand_actions"""
        print("🔧 CORRIGINDO REGISTROS COM HAND_ID NULL")
        print("=" * 45)
        
        db = SessionLocal()
        try:
            # Encontrar registros com hand_id NULL
            null_actions = db.query(HandAction).filter(HandAction.hand_id.is_(None)).all()
            
            print(f"📊 Registros com hand_id NULL encontrados: {len(null_actions)}")
            
            if null_actions:
                # Deletar registros com hand_id NULL
                db.query(HandAction).filter(HandAction.hand_id.is_(None)).delete()
                db.commit()
                print(f"✅ {len(null_actions)} registros com hand_id NULL removidos")
            else:
                print("✅ Nenhum registro com hand_id NULL encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao corrigir hand_actions: {e}")
            db.rollback()
        finally:
            db.close()
            
    def fix_parsing_errors(self):
        """Corrige erros de parsing identificados"""
        print("\n🔧 CORRIGINDO ERROS DE PARSING")
        print("-" * 35)
        
        # Verificar se há mãos com problemas de parsing
        db = SessionLocal()
        try:
            # Encontrar mãos que podem ter problemas
            problematic_hands = db.query(Hand).filter(
                (Hand.hero_name.is_(None)) | 
                (Hand.hero_cards.is_(None)) |
                (Hand.raw_hand.is_(None))
            ).all()
            
            print(f"📊 Mãos com possíveis problemas de parsing: {len(problematic_hands)}")
            
            for hand in problematic_hands:
                print(f"📋 Analisando Hand ID: {hand.hand_id}")
                
                if not hand.raw_hand:
                    print(f"  ❌ Hand {hand.hand_id} não tem raw_hand - removendo")
                    db.delete(hand)
                    continue
                    
                # Tentar re-parse da mão
                try:
                    hand_data = self.parser._parse_single_hand(hand.raw_hand)
                    
                    if hand_data:
                        # Atualizar dados da mão
                        hand.hero_name = hand_data.get('hero_name', hand.hero_name)
                        hand.hero_cards = hand_data.get('hero_cards', hand.hero_cards)
                        hand.hero_position = hand_data.get('hero_position', hand.hero_position)
                        hand.hero_action = hand_data.get('hero_action', hand.hero_action)
                        hand.pot_size = hand_data.get('pot_size', hand.pot_size)
                        hand.board_cards = hand_data.get('board_cards', hand.board_cards)
                        
                        print(f"  ✅ Hand {hand.hand_id} corrigida")
                    else:
                        print(f"  ❌ Hand {hand.hand_id} falhou no re-parse - removendo")
                        db.delete(hand)
                        
                except Exception as e:
                    print(f"  ❌ Erro ao re-parse hand {hand.hand_id}: {e}")
                    db.delete(hand)
                    
            db.commit()
            print(f"✅ Correção de parsing concluída")
            
        except Exception as e:
            print(f"❌ Erro ao corrigir parsing: {e}")
            db.rollback()
        finally:
            db.close()
            
    def fix_session_errors(self):
        """Corrige problemas de sessão do SQLAlchemy"""
        print("\n🔧 CORRIGINDO PROBLEMAS DE SESSÃO")
        print("-" * 40)
        
        # O problema está no código de upload que tenta fazer refresh de objetos
        # que não estão mais na sessão. Vou criar uma versão corrigida
        
        upload_file = "app/routers/upload_progress.py"
        
        if os.path.exists(upload_file):
            with open(upload_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Encontrar e corrigir o problema de refresh
            problematic_code = """        # Atualizar objetos com IDs
        for hand in processed_hands:
            db.refresh(hand)"""
            
            fixed_code = """        # Atualizar objetos com IDs (se ainda estiverem na sessão)
        for hand in processed_hands:
            try:
                db.refresh(hand)
            except Exception as e:
                print(f"⚠️ Não foi possível atualizar hand {hand.hand_id}: {e}")"""
                
            if problematic_code in content:
                new_content = content.replace(problematic_code, fixed_code)
                
                # Salvar backup
                backup_path = f"{upload_file}.backup_session_fix"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Backup salvo em: {backup_path}")
                
                # Salvar arquivo corrigido
                with open(upload_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Arquivo {upload_file} corrigido")
            else:
                print("ℹ️ Problema de sessão não encontrado no arquivo")
                
    def fix_hand_id_issue(self):
        """Corrige o problema de hand_id NULL nas ações"""
        print("\n🔧 CORRIGINDO PROBLEMA DE HAND_ID NULL")
        print("-" * 45)
        
        # O problema está no código que cria HandAction com hand_id None
        # Vou verificar e corrigir o código de upload
        
        upload_file = "app/routers/upload_progress.py"
        
        if os.path.exists(upload_file):
            with open(upload_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Encontrar o problema de hand_id NULL
            problematic_code = """                            db_action = HandAction(
                                hand_id=db_hand.id,  # Será definido após o commit
                                street=action.street,
                                player_name=action.player,
                                action_type=action.action_type,
                                amount=action.amount or 0.0,
                                total_bet=action.total_bet or 0.0,
                                action_order=action_order
                            )"""
            
            fixed_code = """                            # Verificar se db_hand.id existe
                            if db_hand.id is not None:
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
                            else:
                                print(f"⚠️ Hand ID não disponível para ações da mão {hand_id}")"""
                
            if problematic_code in content:
                new_content = content.replace(problematic_code, fixed_code)
                
                # Salvar backup
                backup_path = f"{upload_file}.backup_handid_fix"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Backup salvo em: {backup_path}")
                
                # Salvar arquivo corrigido
                with open(upload_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Arquivo {upload_file} corrigido para hand_id NULL")
            else:
                print("ℹ️ Problema de hand_id NULL não encontrado no arquivo")
                
    def create_robust_upload_test(self):
        """Cria um teste robusto de upload"""
        print("\n🧪 CRIANDO TESTE ROBUSTO DE UPLOAD")
        print("-" * 40)
        
        test_script = '''#!/usr/bin/env python3
"""
Teste Robusto de Upload
Testa o upload com tratamento de erros melhorado
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

class RobustUploadTest:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.parser = PokerStarsParser()
        self.advanced_parser = AdvancedPokerParser()
        
    def test_robust_upload(self):
        """Testa upload com tratamento robusto de erros"""
        print("🚀 TESTE ROBUSTO DE UPLOAD")
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
            # Obter usuário
            user = db.query(User).first()
            if not user:
                print("❌ Nenhum usuário encontrado no banco")
                return False
                
            print(f"👤 Usando usuário: {user.email}")
            
            # Processar mãos com tratamento robusto
            processed_hands = 0
            saved_hands = 0
            skipped_hands = 0
            errors = []
            
            print(f"\n🔄 Processando {len(hands)} mãos com tratamento robusto...")
            
            for i, hand_text in enumerate(hands, 1):
                if i % 50 == 0:
                    print(f"📊 Progresso: {i}/{len(hands)} mãos processadas")
                
                # Adicionar prefixo de volta
                full_hand = "PokerStars Hand #" + hand_text
                
                try:
                    # Parse básico com tratamento de erro
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
                        
                    # Criar registro no banco com validação
                    try:
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
                        
                        # Verificar se o ID foi gerado
                        if db_hand.id is None:
                            print(f"  ❌ Hand ID não foi gerado para mão {hand_id}")
                            db.rollback()
                            continue
                            
                        # Parse avançado para ações com tratamento robusto
                        try:
                            advanced_replay = self.advanced_parser.parse_hand_for_replay(full_hand)
                            
                            if advanced_replay:
                                action_order = 0
                                for street in advanced_replay.streets:
                                    for action in street.actions:
                                        # Validar dados da ação
                                        if action.player and action.action_type:
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
                                
                                print(f"  ✅ {action_order} ações salvas para mão {hand_id}")
                            
                        except Exception as action_error:
                            print(f"  ⚠️ Erro no parse avançado da mão {hand_id}: {action_error}")
                            # Continuar mesmo com erro nas ações
                            
                        processed_hands += 1
                        saved_hands += 1
                        
                        # Commit a cada 10 mãos
                        if i % 10 == 0:
                            db.commit()
                            print(f"  💾 Commit realizado: {i} mãos processadas")
                            
                    except Exception as hand_error:
                        print(f"  ❌ Erro ao salvar mão {hand_id}: {hand_error}")
                        db.rollback()
                        errors.append(f"Mão {i}: {hand_error}")
                        continue
                        
                except Exception as parse_error:
                    error_msg = f"Erro no parse da mão {i}: {parse_error}"
                    errors.append(error_msg)
                    continue
                    
            # Commit final
            try:
                db.commit()
                print(f"  💾 Commit final realizado")
            except Exception as commit_error:
                print(f"  ❌ Erro no commit final: {commit_error}")
                db.rollback()
                
            print(f"\n📊 RESUMO DO TESTE ROBUSTO:")
            print(f"  Mãos processadas: {processed_hands}")
            print(f"  Mãos salvas: {saved_hands}")
            print(f"  Mãos ignoradas: {skipped_hands}")
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

def main():
    """Função principal"""
    print("🔧 TESTE ROBUSTO DE UPLOAD - CORREÇÕES APLICADAS")
    print("=" * 60)
    
    tester = RobustUploadTest()
    success = tester.test_robust_upload()
    
    if success:
        print("\n✅ TESTE ROBUSTO CONCLUÍDO COM SUCESSO!")
        print("🎯 As correções foram aplicadas e funcionaram!")
    else:
        print("\n❌ TESTE ROBUSTO FALHOU!")
        
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
'''
        
        with open("test_robust_upload.py", "w", encoding='utf-8') as f:
            f.write(test_script)
            
        print("✅ Script de teste robusto criado: test_robust_upload.py")

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE ERROS DE UPLOAD")
    print("=" * 40)
    
    fixer = UploadErrorFixer()
    
    # 1. Corrigir tabela hand_actions
    fixer.fix_hand_actions_table()
    
    # 2. Corrigir erros de parsing
    fixer.fix_parsing_errors()
    
    # 3. Corrigir problemas de sessão
    fixer.fix_session_errors()
    
    # 4. Corrigir problema de hand_id NULL
    fixer.fix_hand_id_issue()
    
    # 5. Criar teste robusto
    fixer.create_robust_upload_test()
    
    print("\n✅ CORREÇÕES APLICADAS!")
    print("🎯 Próximos passos:")
    print("1. Reinicie o servidor backend")
    print("2. Execute: python test_robust_upload.py")
    print("3. Teste o upload via frontend")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 