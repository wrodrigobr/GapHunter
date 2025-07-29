#!/usr/bin/env python3
"""
Teste do parser avançado com hand history real
"""

import sys
import os
sys.path.append('/home/ubuntu/gaphunter/backend')

from app.utils.advanced_poker_parser import parse_hand_for_table_replay, AdvancedPokerParser

# Hand history de exemplo
sample_hand = """
*********** # 1 **************
Mão PokerStars #257045862415: Torneio #3910307458, $ 0.98+$ 0.12 USD Hold'em No Limit - Nível V (40/80) - 2025/07/22 10:10:49 ET
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
jojosetubal: coloca ante 10
Kaptahh: coloca ante 10
Andrew Willian: coloca ante 10
Maks19111979: coloca ante 10
SuKKinho: coloca ante 10
petretudor: coloca ante 10
varen1k322: coloca ante 10
Cyan Diogenes: coloca ante 10
phpro: coloca ante 10
Maks19111979: paga o small blind 40
SuKKinho: paga o big blind 80
*** CARTAS DA MÃO ***
phpro recebe [9d Qc]
petretudor: aumenta 546 para 626 e está all-in
varen1k322: desiste
Cyan Diogenes: desiste
phpro: desiste
jojosetubal: desiste
Kaptahh: desiste
Andrew Willian: desiste
Maks19111979: desiste
SuKKinho: desiste
Aposta não-igualada (546) voltou para petretudor
petretudor recebeu 290 do pote
petretudor: não mostra a mão
*** SUMÁRIO ***
Total pote 290 | comissão 0
Lugar 1: jojosetubal desistiu antes Flop (não apostou)
Lugar 2: Kaptahh desistiu antes Flop (não apostou)
Lugar 3: Andrew Willian (Botão) desistiu antes Flop (não apostou)
Lugar 4: Maks19111979 (small blind) desistiu antes Flop
Lugar 5: SuKKinho (big blind) desistiu antes Flop
Lugar 6: petretudor recebeu (290)
Lugar 7: varen1k322 desistiu antes Flop (não apostou)
Lugar 8: Cyan Diogenes desistiu antes Flop (não apostou)
Lugar 9: phpro desistiu antes Flop (não apostou)
"""

def test_parser():
    print("🧪 Testando parser avançado...")
    
    # Teste do parser
    replay_data = parse_hand_for_table_replay(sample_hand)
    
    if not replay_data:
        print("❌ Parser falhou")
        return
    
    print("✅ Parser funcionou!")
    print(f"📊 Hand ID: {replay_data['hand_id']}")
    print(f"🎰 Tournament: {replay_data['tournament_id']}")
    print(f"🪑 Mesa: {replay_data['table_name']}")
    print(f"👤 Herói: {replay_data['hero_name']}")
    print(f"🃏 Cartas do herói: {replay_data['hero_cards']}")
    print(f"💰 Blinds: {replay_data['blinds']}")
    
    print(f"\n👥 Jogadores ({len(replay_data['players'])}):")
    for player in replay_data['players']:
        flags = []
        if player['is_hero']: flags.append('HERÓI')
        if player['is_button']: flags.append('BTN')
        if player['is_sb']: flags.append('SB')
        if player['is_bb']: flags.append('BB')
        
        print(f"  Lugar {player['position']}: {player['name']} ({player['stack']} fichas) {' '.join(flags)}")
    
    print(f"\n🎯 Streets ({len(replay_data['streets'])}):")
    for street in replay_data['streets']:
        print(f"  {street['name'].upper()}: {len(street['actions'])} ações")
        if street['cards']:
            print(f"    Cartas: {street['cards']}")
        for action in street['actions']:
            print(f"    {action['player']}: {action['action']} {action['amount']}")
    
    print(f"\n⚡ Sequência de ações ({len(replay_data['action_sequence'])}):")
    for i, step in enumerate(replay_data['action_sequence'][:10]):  # Primeiros 10
        print(f"  {i+1}. {step['type']}: {step}")
    
    if replay_data['gaps_identified']:
        print(f"\n⚠️ Gaps identificados:")
        for gap in replay_data['gaps_identified']:
            print(f"  - {gap}")
    
    print("\n🎉 Teste concluído com sucesso!")

if __name__ == "__main__":
    test_parser()

