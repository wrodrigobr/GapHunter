#!/usr/bin/env python3
"""
Tradutor de Hand History PokerStars (Português → Inglês)
Para usar durante a importação de dados
"""

import re
from typing import Dict, List, Tuple

class HandHistoryTranslator:
    """Tradutor de hand history do PokerStars"""
    
    def __init__(self):
        self.translations = self._load_translations()
        self.portuguese_indicators = [
            "Mão PokerStars", "Torneio", "Mesa", "Lugar", "é o botão",
            "pequeno blind", "grande blind", "cartas do buraco", "desiste",
            "paga", "aposta", "aumenta", "all-in", "mostra", "ganha"
        ]
        
    def _load_translations(self) -> Dict[str, str]:
        """Carrega o dicionário de traduções"""
        return {
            # Header
            "Mão PokerStars": "PokerStars Hand",
            "Torneio": "Tournament",
            "Mesa": "Table",
            "Lugar": "Seat",
            "é o botão": "is the button",
            "em fichas": "in chips",
            
            # Blinds
            "pequeno blind": "small blind",
            "grande blind": "big blind",
            "posts pequeno blind": "posts small blind",
            "posts grande blind": "posts big blind",
            "posts ante": "posts the ante",
            "coloca ante": "posts the ante",
            "paga o small blind": "posts small blind",
            "paga o big blind": "posts big blind",
            
            # Streets
            "cartas do buraco": "hole cards",
            "cartas da mão": "hole cards",
            "*** CARTAS DO BURACO ***": "*** HOLE CARDS ***",
            "*** CARTAS DA MÃO ***": "*** HOLE CARDS ***",
            "*** FLOP ***": "*** FLOP ***",
            "*** TURNO ***": "*** TURN ***",
            "*** RIO ***": "*** RIVER ***",
            "*** SHOWDOWN ***": "*** SHOWDOWN ***",
            "*** SUMMARY ***": "*** SUMMARY ***",
            "*** SUMÁRIO ***": "*** SUMMARY ***",
            
            # Actions
            "desiste": "folds",
            "paga": "calls",
            "iguala": "calls",
            "aposta": "bets",
            "aumenta": "raises",
            "passa": "checks",
            "all-in": "all-in",
            "mostra": "shows",
            "ganha": "wins",
            "coleta": "collected",
            "recebeu": "collected",
            "aposta não chamada": "Uncalled bet",
            "aposta não-igualada": "Uncalled bet",
            "retorna": "returned",
            "voltou": "returned",
            "não mostra a mão": "doesn't show hand",
            "terminou o torneio": "finished the tournament",
            "e recebeu": "and received",
            "lugar": "place",
            "perde": "lost",
            "está sem ligação": "is disconnected",
            
            # Cards
            "Dealt to": "Dealt to",
            "Board": "Board",
            "Distribuído para": "Dealt to",
            "recebe": "Dealt to",
            
            # Summary
            "Total pot": "Total pot",
            "Total pote": "Total pot",
            "Rake": "Rake",
            "comissão": "Rake",
            "folded on the": "folded on the",
            "showed and won": "showed and won",
            "folded before": "folded before",
            "desistiu antes": "folded before",
            "desistiu no": "folded on the",
            "didn't bet": "didn't bet",
            "não apostou": "didn't bet",
            
            # Tournament specific
            "Nível": "Level",
            "USD": "USD",
            "Hold'em No Limit": "Hold'em No Limit",
            "9-max": "9-max",
            "6-max": "6-max",
            "heads-up": "heads-up"
        }
    
    def detect_language(self, hand_text: str) -> str:
        """Detecta se o hand history está em português ou inglês"""
        portuguese_indicators = [
            "Mão PokerStars", "Torneio", "Mesa", "Lugar", "é o botão",
            "pequeno blind", "grande blind", "cartas do buraco", "cartas da mão",
            "desiste", "paga", "aposta", "aumenta", "passa", "iguala",
            "all-in", "mostra", "ganha", "coloca ante", "paga o small blind",
            "paga o big blind", "recebe", "não mostra a mão", "SUMÁRIO",
            "comissão", "desistiu", "não apostou", "está sem ligação"
        ]
        
        english_indicators = [
            "PokerStars Hand", "Tournament", "Table", "Seat", "is the button",
            "small blind", "big blind", "hole cards", "folds", "calls",
            "bets", "raises", "checks", "all-in", "shows", "wins",
            "posts the ante", "posts small blind", "posts big blind",
            "Dealt to", "doesn't show hand", "SUMMARY", "Rake",
            "folded", "didn't bet", "is disconnected"
        ]
        
        portuguese_count = sum(1 for indicator in portuguese_indicators if indicator in hand_text)
        english_count = sum(1 for indicator in english_indicators if indicator in hand_text)
        
        if portuguese_count > english_count:
            return "portuguese"
        else:
            return "english"
    
    def translate_hand_history(self, hand_text: str) -> str:
        """Traduz hand history de português para inglês"""
        
        # Detectar idioma
        language = self.detect_language(hand_text)
        if language == "english":
            return hand_text  # Já está em inglês
        
        print(f"🌍 Detectado: {language.upper()} → Convertendo para inglês...")
        
        # Aplicar traduções
        translated_text = hand_text
        
        # Traduções específicas por padrão
        for portuguese, english in self.translations.items():
            translated_text = translated_text.replace(portuguese, english)
        
        # Traduções com regex para casos mais complexos
        translated_text = self._apply_regex_translations(translated_text)
        
        # Verificar se a tradução foi bem-sucedida
        if self._validate_translation(translated_text):
            print("✅ Tradução concluída com sucesso!")
            return translated_text
        else:
            print("⚠️  Tradução pode ter problemas - verificar manualmente")
            return translated_text
    
    def _apply_regex_translations(self, text: str) -> str:
        """Aplica traduções que precisam de regex"""
        
        # Traduzir "coloca ante X" → "posts the ante X"
        text = re.sub(r'(\w+): coloca ante (\d+(?:\.\d+)?)', r'\1: posts the ante \2', text)
        
        # Traduzir "paga o small blind X" → "posts small blind X"
        text = re.sub(r'(\w+): paga o small blind (\d+(?:\.\d+)?)', r'\1: posts small blind \2', text)
        
        # Traduzir "paga o big blind X" → "posts big blind X"
        text = re.sub(r'(\w+): paga o big blind (\d+(?:\.\d+)?)', r'\1: posts big blind \2', text)
        
        # Traduzir "posts pequeno blind X" → "posts small blind X" (padrão antigo)
        text = re.sub(r'(\w+): posts pequeno blind (\d+(?:\.\d+)?)', r'\1: posts small blind \2', text)
        text = re.sub(r'(\w+): posts grande blind (\d+(?:\.\d+)?)', r'\1: posts big blind \2', text)
        
        # Traduzir "posts ante X" → "posts the ante X" (padrão antigo)
        text = re.sub(r'(\w+): posts ante (\d+(?:\.\d+)?)', r'\1: posts the ante \2', text)
        
        # Traduzir "Lugar X: Nome (Y em fichas)" → "Seat X: Nome (Y in chips)"
        text = re.sub(r'Lugar (\d+): ([^(]+) \((\d+(?:\.\d+)?) em fichas\)', r'Seat \1: \2 (\3 in chips)', text)
        
        # Traduzir "Mesa 'Nome' X-max" → "Table 'Nome' X-max"
        text = re.sub(r'Mesa \'([^\']+)\' (\d+)-max', r'Table \'\1\' \2-max', text)
        
        # Traduzir "Nível X (Y/Z)" → "Level X (Y/Z)"
        text = re.sub(r'Nível (\w+) \((\d+)/(\d+)\)', r'Level \1 (\2/\3)', text)
        
        # Traduzir "*** CARTAS DA MÃO ***" → "*** HOLE CARDS ***"
        text = re.sub(r'\*\*\* CARTAS DA MÃO \*\*\*', r'*** HOLE CARDS ***', text)
        
        # Traduzir "recebe [cartas]" → "Dealt to [cartas]"
        text = re.sub(r'(\w+) recebe \[([^\]]+)\]', r'Dealt to \1 [\2]', text)
        
        # Traduzir ações com valores
        text = re.sub(r'(\w+) desiste', r'\1 folds', text)
        text = re.sub(r'(\w+) iguala (\d+(?:\.\d+)?)', r'\1 calls \2', text)
        text = re.sub(r'(\w+) paga (\d+(?:\.\d+)?)', r'\1 calls \2', text)
        text = re.sub(r'(\w+) aposta (\d+(?:\.\d+)?)', r'\1 bets \2', text)
        text = re.sub(r'(\w+) aumenta (\d+(?:\.\d+)?) para (\d+(?:\.\d+)?)', r'\1 raises \2 to \3', text)
        text = re.sub(r'(\w+) all-in (\d+(?:\.\d+)?)', r'\1 all-in \2', text)
        text = re.sub(r'(\w+) passa', r'\1 checks', text)
        
        # Traduzir "e está all-in" → "and is all-in"
        text = re.sub(r' e está all-in', r' and is all-in', text)
        
        # Traduzir "Aposta não-igualada" → "Uncalled bet"
        text = re.sub(r'Aposta não-igualada', r'Uncalled bet', text)
        
        # Traduzir "voltou para" → "returned to"
        text = re.sub(r'voltou para (\w+)', r'returned to \1', text)
        
        # Traduzir "recebeu X do pote" → "collected X from pot"
        text = re.sub(r'(\w+) recebeu (\d+(?:\.\d+)?) do pote', r'\1 collected \2 from pot', text)
        
        # Traduzir "não mostra a mão" → "doesn't show hand"
        text = re.sub(r'(\w+): não mostra a mão', r'\1: doesn\'t show hand', text)
        
        # Traduzir "*** SUMÁRIO ***" → "*** SUMMARY ***"
        text = re.sub(r'\*\*\* SUMÁRIO \*\*\*', r'*** SUMMARY ***', text)
        
        # Traduzir "Total pote" → "Total pot"
        text = re.sub(r'Total pote', r'Total pot', text)
        
        # Traduzir "comissão" → "Rake"
        text = re.sub(r'comissão', r'Rake', text)
        
        # Traduzir "Mesa [cartas]" → "Board [cartas]"
        text = re.sub(r'Mesa \[([^\]]+)\]', r'Board [\1]', text)
        
        # Traduzir "desistiu antes Flop" → "folded before Flop"
        text = re.sub(r'desistiu antes Flop', r'folded before Flop', text)
        
        # Traduzir "não apostou" → "didn't bet"
        text = re.sub(r'não apostou', r'didn\'t bet', text)
        
        # Traduzir "desistiu no" → "folded on the"
        text = re.sub(r'desistiu no (\w+)', r'folded on the \1', text)
        
        # Traduzir "recebeu (X)" → "collected (X)"
        text = re.sub(r'recebeu \((\d+(?:\.\d+)?)\)', r'collected (\1)', text)
        
        # Traduzir "(Botão)" → "(button)"
        text = re.sub(r'\(Botão\)', r'(button)', text)
        
        # Traduzir "(small blind)" → "(small blind)"
        text = re.sub(r'\(small blind\)', r'(small blind)', text)
        
        # Traduzir "(big blind)" → "(big blind)"
        text = re.sub(r'\(big blind\)', r'(big blind)', text)
        
        # Traduzir "está sem ligação" → "is disconnected"
        text = re.sub(r'está sem ligação', r'is disconnected', text)
        
        return text
    
    def _validate_translation(self, translated_text: str) -> bool:
        """Valida se a tradução foi bem-sucedida"""
        
        # Verificar se contém elementos essenciais do PokerStars em inglês
        required_elements = [
            "PokerStars Hand",
            "Hold'em No Limit",
            "Table",
            "Seat",
            "is the button",
            "posts small blind",
            "posts big blind",
            "*** HOLE CARDS ***",
            "Dealt to"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in translated_text:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️  Elementos faltando após tradução: {missing_elements}")
            return False
        
        return True
    
    def process_hand_for_import(self, hand_text: str) -> Tuple[str, str]:
        """Processa hand history para importação, retornando (texto_processado, idioma_detectado)"""
        
        # Detectar idioma
        language = self.detect_language(hand_text)
        
        # Traduzir se necessário
        if language == "portuguese":
            processed_text = self.translate_hand_history(hand_text)
        else:
            processed_text = hand_text
        
        return processed_text, language

def test_translator():
    """Testa o tradutor com uma amostra"""
    
    translator = HandHistoryTranslator()
    
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
    
    print("🧪 TESTE DO TRADUTOR")
    print("=" * 50)
    
    # Detectar idioma
    language = translator.detect_language(portuguese_hand)
    print(f"🌍 Idioma detectado: {language}")
    
    # Traduzir
    english_hand = translator.translate_hand_history(portuguese_hand)
    
    print("\n📋 COMPARAÇÃO:")
    print("\n--- PORTUGUÊS ---")
    print(portuguese_hand[:500] + "...")
    
    print("\n--- INGLÊS ---")
    print(english_hand[:500] + "...")
    
    # Validar
    is_valid = translator._validate_translation(english_hand)
    print(f"\n✅ Tradução válida: {is_valid}")

if __name__ == "__main__":
    test_translator() 