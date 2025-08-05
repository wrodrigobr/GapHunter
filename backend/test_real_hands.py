#!/usr/bin/env python3
"""
Teste do tradutor com hand histories reais do PokerStars
"""

from hand_history_translator import HandHistoryTranslator

def test_real_hands():
    """Testa o tradutor com hand histories reais"""
    
    translator = HandHistoryTranslator()
    
    # Hand history real #1
    hand1_portuguese = """Mão PokerStars #257045862415: Torneio #3910307458, $ 0.98+$ 0.12 USD Hold'em No Limit - Nível V (40/80) - 2025/07/22 10:10:49 ET
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
Lugar 9: phpro desistiu antes Flop (não apostou)"""
    
    # Hand history real #2
    hand2_portuguese = """Mão PokerStars #257045867083: Torneio #3910307458, $ 0.98+$ 0.12 USD Hold'em No Limit - Nível V (40/80) - 2025/07/22 10:11:21 ET
Mesa '3910307458 12' 9-max Lugar #4 é o botão
Lugar 1: jojosetubal (7825 em fichas)
Lugar 2: Kaptahh (8367 em fichas)
Lugar 3: Andrew Willian (1779 em fichas)
Lugar 4: Maks19111979 (2850 em fichas)
Lugar 5: SuKKinho (3968 em fichas)
Lugar 7: varen1k322 (2794 em fichas)
Lugar 8: Cyan Diogenes (9030 em fichas)
Lugar 9: phpro (2990 em fichas)
jojosetubal: coloca ante 10
Kaptahh: coloca ante 10
Andrew Willian: coloca ante 10
Maks19111979: coloca ante 10
SuKKinho: coloca ante 10
varen1k322: coloca ante 10
Cyan Diogenes: coloca ante 10
phpro: coloca ante 10
SuKKinho: paga o small blind 40
varen1k322: paga o big blind 80
*** CARTAS DA MÃO ***
phpro recebe [9d 7c]
Cyan Diogenes: desiste
phpro: desiste
jojosetubal: desiste
Kaptahh: desiste
Andrew Willian: desiste
Maks19111979: aumenta 80 para 160
SuKKinho: desiste
varen1k322: iguala 80
*** FLOP *** [Ts 2c 9c]
varen1k322: passa
martelli1990 está sem ligação
Maks19111979: passa
*** TURN *** [Ts 2c 9c] [Jc]
varen1k322: aposta 225
Maks19111979: desiste
Aposta não-igualada (225) voltou para varen1k322
varen1k322 recebeu 440 do pote
*** SUMÁRIO ***
Total pote 440 | comissão 0
Mesa [Ts 2c 9c Jc]
Lugar 1: jojosetubal desistiu antes Flop (não apostou)
Lugar 2: Kaptahh desistiu antes Flop (não apostou)
Lugar 3: Andrew Willian desistiu antes Flop (não apostou)
Lugar 4: Maks19111979 (Botão) desistiu no Turn
Lugar 5: SuKKinho (small blind) desistiu antes Flop
Lugar 7: varen1k322 (big blind) recebeu (440)
Lugar 8: Cyan Diogenes desistiu antes Flop (não apostou)
Lugar 9: phpro desistiu antes Flop (não apostou)"""
    
    print("🧪 TESTE COM HAND HISTORIES REAIS")
    print("=" * 60)
    
    # Testar Hand #1
    print("\n📋 HAND #1 - TESTE DE TRADUÇÃO")
    print("-" * 40)
    
    # Detectar idioma
    language1 = translator.detect_language(hand1_portuguese)
    print(f"🌍 Idioma detectado: {language1}")
    
    # Traduzir
    hand1_english = translator.translate_hand_history(hand1_portuguese)
    
    print("\n📋 COMPARAÇÃO HAND #1:")
    print("\n--- PORTUGUÊS (primeiras linhas) ---")
    lines1_pt = hand1_portuguese.split('\n')[:15]
    for i, line in enumerate(lines1_pt, 1):
        print(f"{i:2d}: {line}")
    
    print("\n--- INGLÊS (primeiras linhas) ---")
    lines1_en = hand1_english.split('\n')[:15]
    for i, line in enumerate(lines1_en, 1):
        print(f"{i:2d}: {line}")
    
    # Validar
    is_valid1 = translator._validate_translation(hand1_english)
    print(f"\n✅ Hand #1 válida: {is_valid1}")
    
    # Testar Hand #2
    print("\n📋 HAND #2 - TESTE DE TRADUÇÃO")
    print("-" * 40)
    
    # Detectar idioma
    language2 = translator.detect_language(hand2_portuguese)
    print(f"🌍 Idioma detectado: {language2}")
    
    # Traduzir
    hand2_english = translator.translate_hand_history(hand2_portuguese)
    
    print("\n📋 COMPARAÇÃO HAND #2:")
    print("\n--- PORTUGUÊS (primeiras linhas) ---")
    lines2_pt = hand2_portuguese.split('\n')[:15]
    for i, line in enumerate(lines2_pt, 1):
        print(f"{i:2d}: {line}")
    
    print("\n--- INGLÊS (primeiras linhas) ---")
    lines2_en = hand2_english.split('\n')[:15]
    for i, line in enumerate(lines2_en, 1):
        print(f"{i:2d}: {line}")
    
    # Validar
    is_valid2 = translator._validate_translation(hand2_english)
    print(f"\n✅ Hand #2 válida: {is_valid2}")
    
    # Salvar resultados para teste no RIROPO
    with open('test_hand1_english.txt', 'w', encoding='utf-8') as f:
        f.write(hand1_english)
    
    with open('test_hand2_english.txt', 'w', encoding='utf-8') as f:
        f.write(hand2_english)
    
    print(f"\n💾 Hand histories traduzidos salvos em:")
    print(f"   - test_hand1_english.txt")
    print(f"   - test_hand2_english.txt")
    print(f"\n💡 Você pode testar estes arquivos diretamente no RIROPO!")

if __name__ == "__main__":
    test_real_hands() 