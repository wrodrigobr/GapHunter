#!/usr/bin/env python3
"""
Validador de Hand History - Exige formato em inglês
"""

import re
from typing import Dict, List, Tuple

class HandHistoryValidator:
    """Validador que exige hand history em inglês"""
    
    def __init__(self):
        self.required_english_elements = [
            "PokerStars Hand",
            "Tournament", 
            "Table",
            "Seat",
            "is the button",
            "posts small blind",
            "posts big blind",
            "posts the ante",
            "*** HOLE CARDS ***",
            "Dealt to",
            "folds",
            "calls",
            "bets",
            "raises",
            "checks",
            "all-in",
            "shows",
            "collected",
            "Uncalled bet",
            "returned to",
            "*** SUMMARY ***",
            "Total pot",
            "Rake",
            "Board",
            "folded",
            "won",
            "lost",
            "finished the tournament"
        ]
        
        # Elementos mínimos obrigatórios para considerar válido
        self.minimum_required_elements = [
            "PokerStars Hand",
            "Table",
            "Seat",
            "*** HOLE CARDS ***"
        ]
        
        self.portuguese_indicators = [
            "Mão PokerStars",
            "Torneio",
            "Mesa", 
            "Lugar",
            "é o botão",
            "pequeno blind",
            "grande blind",
            "coloca ante",
            "paga o small blind",
            "paga o big blind",
            "*** CARTAS DA MÃO ***",
            "*** CARTAS DO BURACO ***",
            "recebe",
            "Distribuído para",
            "desiste",
            "paga",
            "aposta",
            "aumenta",
            "passa",
            "iguala",
            "mostra",
            "recebeu",
            "coleta",
            "Aposta não-igualada",
            "voltou para",
            "*** SUMÁRIO ***",
            "Total pote",
            "comissão",
            "Mesa [",
            "desistiu",
            "não apostou",
            "ganha",
            "perde",
            "terminou o torneio"
        ]
        
        self.spanish_indicators = [
            "Mano PokerStars",
            "Torneo",
            "Mesa",
            "Asiento",
            "es el botón",
            "pequeña ciega",
            "gran ciega",
            "publica ante",
            "*** CARTAS AGUJERO ***",
            "Repartido a",
            "se retira",
            "paga",
            "apuesta",
            "sube",
            "pasa",
            "iguala",
            "muestra",
            "recibe",
            "Apuesta no igualada",
            "devuelto a",
            "*** RESUMEN ***",
            "Bote total",
            "Comisión",
            "Mesa [",
            "se retiró",
            "no apostó"
        ]
    
    def validate_hand_history(self, hand_text: str) -> Tuple[bool, str, str]:
        """
        Valida se o hand history está em inglês
        Retorna: (is_valid, language_detected, error_message)
        """
        
        if not hand_text or not hand_text.strip():
            return False, "unknown", "Hand history está vazio"
        
        # Detectar idioma
        language = self._detect_language(hand_text)
        
        if language == "english":
            # Verificar se contém elementos essenciais
            missing_elements = self._check_required_elements(hand_text)
            
            if missing_elements:
                return False, "english", f"Hand history em inglês mas faltando elementos essenciais: {', '.join(missing_elements[:5])}"
            
            return True, "english", "Hand history válido em inglês"
        
        else:
            # Gerar erro específico para o idioma detectado
            error_message = self._generate_language_error(language)
            return False, language, error_message
    
    def _detect_language(self, hand_text: str) -> str:
        """Detecta o idioma do hand history"""
        
        portuguese_count = sum(1 for indicator in self.portuguese_indicators if indicator in hand_text)
        spanish_count = sum(1 for indicator in self.spanish_indicators if indicator in hand_text)
        english_count = sum(1 for indicator in self.required_english_elements if indicator in hand_text)
        
        if portuguese_count > english_count and portuguese_count > spanish_count:
            return "portuguese"
        elif spanish_count > english_count and spanish_count > portuguese_count:
            return "spanish"
        elif english_count > portuguese_count and english_count > spanish_count:
            return "english"
        else:
            return "unknown"
    
    def _check_required_elements(self, hand_text: str) -> List[str]:
        """Verifica se contém elementos essenciais do PokerStars em inglês"""
        
        missing_elements = []
        for element in self.minimum_required_elements:
            if element not in hand_text:
                missing_elements.append(element)
        
        return missing_elements
    
    def _generate_language_error(self, language: str) -> str:
        """Gera mensagem de erro específica para o idioma"""
        
        if language == "portuguese":
            return """❌ HAND HISTORY EM PORTUGUÊS DETECTADO

O arquivo contém hand history em português, mas o sistema exige formato em inglês.

🔧 SOLUÇÕES:
1. Configure o PokerStars para exportar hand history em inglês:
   - Abra o PokerStars
   - Vá em Configurações > Interface
   - Altere o idioma para "English"
   - Reexporte os hand histories

2. Use um tradutor online para converter português → inglês

3. Aguarde a próxima versão que suportará múltiplos idiomas

📋 EXEMPLO DE FORMATO CORRETO:
PokerStars Hand #123456789: Tournament #987654321, $1.00+$0.10 USD Hold'em No Limit - Level I (10/20) - 2025/01/01 12:00:00 ET
Table 'Tournament 123' 9-max Seat #1 is the button
Seat 1: Player1 (1000 in chips)
Seat 2: Player2 (1000 in chips)
Player1: posts small blind 10
Player2: posts big blind 20
*** HOLE CARDS ***
Dealt to Player1 [Ah Kh]
Player1: raises 40 to 60
Player2: calls 40"""

        elif language == "spanish":
            return """❌ HAND HISTORY EM ESPANHOL DETECTADO

O arquivo contém hand history em espanhol, mas o sistema exige formato em inglês.

🔧 SOLUÇÕES:
1. Configure o PokerStars para exportar hand history em inglês
2. Use um tradutor online para converter espanhol → inglês
3. Aguarde a próxima versão que suportará múltiplos idiomas"""

        else:
            return """❌ FORMATO DE HAND HISTORY NÃO RECONHECIDO

O arquivo não parece ser um hand history válido do PokerStars em inglês.

📋 VERIFIQUE:
- O arquivo contém hand history do PokerStars?
- O formato está em inglês?
- O arquivo não está corrompido?

📋 EXEMPLO DE FORMATO CORRETO:
PokerStars Hand #123456789: Tournament #987654321, $1.00+$0.10 USD Hold'em No Limit - Level I (10/20) - 2025/01/01 12:00:00 ET
Table 'Tournament 123' 9-max Seat #1 is the button
Seat 1: Player1 (1000 in chips)
Seat 2: Player2 (1000 in chips)
Player1: posts small blind 10
Player2: posts big blind 20
*** HOLE CARDS ***
Dealt to Player1 [Ah Kh]
Player1: raises 40 to 60
Player2: calls 40"""
    
    def get_supported_formats(self) -> str:
        """Retorna informações sobre formatos suportados"""
        return """📋 FORMATOS SUPORTADOS:

✅ ATUALMENTE SUPORTADO:
- PokerStars Hand History em inglês

🔄 EM DESENVOLVIMENTO:
- PokerStars Hand History em português
- PokerStars Hand History em espanhol
- Hand histories de outros sites (888, PartyPoker, etc.)

💡 DICA:
Configure o PokerStars para exportar hand history em inglês para compatibilidade total."""

def test_validator():
    """Testa o validador com exemplos"""
    
    validator = HandHistoryValidator()
    
    # Exemplo em inglês (válido)
    english_hand = """PokerStars Hand #257152142480: Tournament #3914216809, $0.85+$0.15 USD Hold'em No Limit - Level VI (80/160) - 2025/07/30 20:13:26 ET
Table '3914216809 1' 9-max Seat #5 is the button
Seat 2: mucareca10 (1698 in chips)
Seat 4: phpro (1366 in chips)
Seat 5: Vinao182 (10436 in chips)
mucareca10: posts the ante 20
phpro: posts the ante 20
Vinao182: posts the ante 20
mucareca10: posts small blind 80
phpro: posts big blind 160
*** HOLE CARDS ***
Dealt to phpro [Qd Ks]
Vinao182: folds
mucareca10: raises 1518 to 1678 and is all-in
phpro: calls 1186 and is all-in
Uncalled bet (332) returned to mucareca10"""
    
    # Exemplo em português (inválido)
    portuguese_hand = """Mão PokerStars #257045862415: Torneio #3910307458, $ 0.98+$ 0.12 USD Hold'em No Limit - Nível V (40/80) - 2025/07/22 10:10:49 ET
Mesa '3910307458 12' 9-max Lugar #3 é o botão
Lugar 1: jojosetubal (7835 em fichas)
jojosetubal: coloca ante 10
*** CARTAS DA MÃO ***
phpro recebe [9d Qc]
petretudor: aumenta 546 para 626 e está all-in"""
    
    print("🧪 TESTE DO VALIDADOR")
    print("=" * 50)
    
    # Testar hand em inglês
    print("\n📋 TESTE 1: Hand History em Inglês")
    print("-" * 40)
    is_valid1, lang1, msg1 = validator.validate_hand_history(english_hand)
    print(f"✅ Válido: {is_valid1}")
    print(f"🌍 Idioma: {lang1}")
    print(f"💬 Mensagem: {msg1}")
    
    # Testar hand em português
    print("\n📋 TESTE 2: Hand History em Português")
    print("-" * 40)
    is_valid2, lang2, msg2 = validator.validate_hand_history(portuguese_hand)
    print(f"✅ Válido: {is_valid2}")
    print(f"🌍 Idioma: {lang2}")
    print(f"💬 Mensagem: {msg2}")
    
    # Mostrar formatos suportados
    print("\n📋 FORMATOS SUPORTADOS")
    print("-" * 40)
    print(validator.get_supported_formats())

if __name__ == "__main__":
    test_validator() 