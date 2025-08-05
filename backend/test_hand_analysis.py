#!/usr/bin/env python3
"""
Teste de Análise da Mão #257152017277
Verifica se o parser está capturando todas as ações corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.poker_parser import PokerStarsParser
from app.utils.advanced_poker_parser import AdvancedPokerParser

def test_hand_257152017277():
    """Testa a mão específica #257152017277"""
    
    hand_text = """PokerStars Hand #257152017277: Tournament #3914216809, $0.85+$0.15 USD Hold'em No Limit - Level IV (40/80) - 2025/07/30 20:00:03 ET
Table '3914216809 1' 9-max Seat #1 is the button
Seat 1: TaksMann (1684 in chips)
Seat 2: mucareca10 (1913 in chips)
Seat 4: phpro (1495 in chips)
Seat 5: Vinao182 (1515 in chips)
Seat 6: Portos1941 (1382 in chips)
Seat 7: Biduu 1985 (2430 in chips)
Seat 8: zagroba_cwb (1839 in chips)
Seat 9: Tribst (1242 in chips)
TaksMann: posts the ante 10
mucareca10: posts the ante 10
phpro: posts the ante 10
Vinao182: posts the ante 10
Portos1941: posts the ante 10
Biduu 1985: posts the ante 10
zagroba_cwb: posts the ante 10
Tribst: posts the ante 10
mucareca10: posts small blind 40
phpro: posts big blind 80
*** HOLE CARDS ***
Dealt to phpro [Qh 9s]
Vinao182: raises 160 to 240
Portos1941: calls 240
Biduu 1985: folds
zagroba_cwb: folds
Tribst: folds
TaksMann: folds
mucareca10: folds
phpro: folds
*** FLOP *** [7s 3d 2d]
Vinao182: checks
Portos1941: bets 240
Vinao182: raises 1025 to 1265 and is all-in
Portos1941: calls 892 and is all-in
Uncalled bet (133) returned to Vinao182
*** TURN *** [7s 3d 2d] [7d]
*** RIVER *** [7s 3d 2d 7d] [8c]
*** SHOW DOWN ***
Vinao182: shows [8s 8d] (a full house, Eights full of Sevens)
Portos1941: shows [Ah 6h] (a pair of Sevens)
Vinao182 collected 2944 from pot
Portos1941 finished the tournament in 8th place
*** SUMMARY ***
Total pot 2944 | Rake 0
Board [7s 3d 2d 7d 8c]
Seat 1: TaksMann (button) folded before Flop (didn't bet)
Seat 2: mucareca10 (small blind) folded before Flop
Seat 4: phpro (big blind) folded before Flop
Seat 5: Vinao182 showed [8s 8d] and won (2944) with a full house, Eights full of Sevens
Seat 6: Portos1941 showed [Ah 6h] and lost with a pair of Sevens
Seat 7: Biduu 1985 folded before Flop (didn't bet)
Seat 8: zagroba_cwb folded before Flop (didn't bet)
Seat 9: Tribst folded before Flop (didn't bet)"""

    print("🧪 ANÁLISE DA MÃO #257152017277")
    print("=" * 50)
    
    # Teste 1: Parser básico
    print("\n📋 Teste 1: Parser Básico")
    print("-" * 30)
    
    parser = PokerStarsParser()
    hands = parser.parse_file(hand_text)
    
    if hands:
        hand = hands[0]
        print(f"✅ Mão encontrada: {hand['hand_id']}")
        print(f"📊 Tournament: {hand['tournament_id']}")
        print(f"📋 Table: {hand['table_name']}")
        print(f"🎯 Pot: ${hand['pot_size']}")
        print(f"🃏 Board: {hand['board_cards']}")
        print(f"👤 Hero: {hand['hero_name']} - {hand['hero_cards']} - {hand['hero_action']}")
    else:
        print("❌ Nenhuma mão encontrada pelo parser básico")
    
    # Teste 2: Parser avançado
    print("\n📋 Teste 2: Parser Avançado")
    print("-" * 30)
    
    advanced_parser = AdvancedPokerParser()
    replay_data = advanced_parser.parse_hand_for_replay(hand_text)
    
    if replay_data:
        print(f"✅ Replay data gerada com sucesso!")
        print(f"📊 Hand ID: {replay_data.hand_id}")
        print(f"🎯 Tournament: {replay_data.tournament_id}")
        print(f"📋 Table: {replay_data.table_name}")
        print(f"🃏 Hero Cards: {replay_data.hero_cards}")
        print(f"👥 Players: {len(replay_data.players)}")
        print(f"🎯 Streets: {len(replay_data.streets)}")
        
        print("\n👥 Jogadores:")
        for player in replay_data.players:
            status = []
            if getattr(player, 'is_button', False): status.append('BTN')
            if getattr(player, 'is_small_blind', False): status.append('SB')
            if getattr(player, 'is_big_blind', False): status.append('BB')
            if getattr(player, 'is_hero', False): status.append('HERÓI')
            status_str = ' '.join(status) if status else ''
            print(f"   {player.name}: ${player.stack} {status_str}")
        
        print("\n🎯 Streets e Ações:")
        for street in replay_data.streets:
            print(f"\n   {street.name.upper()}: {len(street.actions)} ações")
            if hasattr(street, 'cards') and street.cards:
                print(f"     Cartas: {street.cards}")
            for action in street.actions:
                amount_str = f" ${getattr(action, 'amount', 0)}" if getattr(action, 'amount', 0) else ""
                print(f"     {action.player}: {action.action_type}{amount_str}")
    else:
        print("❌ Falha ao gerar replay data")
    
    # Teste 3: Verificação de ações específicas
    print("\n📋 Teste 3: Verificação de Ações Específicas")
    print("-" * 30)
    
    expected_actions = [
        # Preflop
        ("Vinao182", "raise", 160),
        ("Portos1941", "call", 240),
        ("Biduu 1985", "fold", 0),
        ("zagroba_cwb", "fold", 0),
        ("Tribst", "fold", 0),
        ("TaksMann", "fold", 0),
        ("mucareca10", "fold", 0),
        ("phpro", "fold", 0),
        # Flop
        ("Vinao182", "check", 0),
        ("Portos1941", "bet", 240),
        ("Vinao182", "raise", 1025),
        ("Portos1941", "call", 892),
        # Turn (sem ações)
        # River (sem ações)
        # Summary
        ("Vinao182", "collected", 2944)
    ]
    
    if replay_data:
        actual_actions = []
        for street in replay_data['streets']:
            for action in street['actions']:
                actual_actions.append((
                    action['player'],
                    action['action'],
                    action.get('amount', 0)
                ))
        
        print(f"✅ Ações encontradas: {len(actual_actions)}")
        print(f"🎯 Ações esperadas: {len(expected_actions)}")
        
        print("\n📊 Comparação:")
        for i, (expected, actual) in enumerate(zip(expected_actions, actual_actions)):
            status = "✅" if expected == actual else "❌"
            print(f"   {status} {i+1:2d}. {expected[0]}: {expected[1]} ${expected[2]} | {actual[0]}: {actual[1]} ${actual[2]}")
        
        if len(actual_actions) < len(expected_actions):
            print(f"\n⚠️  Faltam {len(expected_actions) - len(actual_actions)} ações")
            for i in range(len(actual_actions), len(expected_actions)):
                print(f"   ❌ {expected_actions[i]}")
    
    print("\n🎉 ANÁLISE CONCLUÍDA!")

if __name__ == "__main__":
    test_hand_257152017277() 