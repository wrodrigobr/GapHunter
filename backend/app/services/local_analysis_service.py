import json
from typing import Dict, Any


class LocalAnalysisService:
    def __init__(self):
        # Carrega todos os ranges na memória
        with open("ranges/open_raise.json") as f:
            self.open_raise_ranges = json.load(f)

        with open("ranges/push_fold.json") as f:
            self.push_fold_ranges = json.load(f)

        with open("ranges/3bet.json") as f:
            self.three_bet_ranges = json.load(f)

    def get_stack_category(self, stack: float) -> str:
        """
        Retorna categoria de stack: short_stack, mid_stack ou deep_stack.
        """
        if stack <= 15:
            return "short_stack"
        elif stack <= 30:
            return "mid_stack"
        else:
            return "deep_stack"

    def get_push_fold_level(self, stack: float) -> str:
        """
        Retorna nível push/fold (8bb, 10bb).
        """
        if stack <= 8:
            return "8bb"
        elif stack <= 10:
            return "10bb"
        return "10bb"

    async def analyze_hand_locally(self, hand_data: Dict[str, Any]) -> str:
        """
        Realiza análise local baseada em ranges ABC Poker + stack + posição.
        Retorna texto pronto para ser gravado no banco.
        """
        hero_position = hand_data.get("hero_position", "UTG").upper()
        hero_cards = hand_data.get("hero_cards", "").replace(" ", "").upper()
        hero_action = hand_data.get("hero_action", "").lower()
        hero_stack = hand_data.get("hero_stack", 0)
        pot_size = hand_data.get("pot_size", 0)

        # ====== Categoria do stack
        stack_cat = self.get_stack_category(hero_stack)
        push_fold_level = self.get_push_fold_level(hero_stack)

        # ====== Ranges
        open_range = self.open_raise_ranges.get(stack_cat, {}).get(hero_position, [])
        push_fold_range = self.push_fold_ranges.get(push_fold_level, {}).get(hero_position, [])

        # ====== Diagnóstico
        in_open_range = hero_cards in open_range
        in_push_fold_range = hero_cards in push_fold_range

        range_comment = ""
        if hero_stack <= 15:
            if in_push_fold_range:
                range_comment = "✅ Mão dentro do range de push/fold."
            else:
                range_comment = "⚠️ Mão fora do range push/fold — ajuste necessário."
        else:
            if in_open_range:
                range_comment = "✅ Mão dentro do range de open raise."
            else:
                range_comment = "⚠️ Mão fora do range open raise para essa posição."

        # ====== Coerência posição + ação
        position_action_comment = ""
        if hero_position in ["UTG", "UTG+1", "MP", "EARLY"]:
            if hero_action in ["call", "limp"]:
                position_action_comment = "⚠️ Jogada passiva em posição inicial é geralmente ruim. Prefira raise ou fold."
            elif hero_action == "raise":
                position_action_comment = "✅ Ação agressiva é coerente com posição inicial, contanto que respeite range tight."
        elif hero_position in ["CO", "BTN", "LATE"]:
            if hero_action == "raise":
                position_action_comment = "✅ Agressividade correta em posição final."
            elif hero_action == "call":
                position_action_comment = "🟢 Call pode ser ok em posição final, avalie odds e adversários."

        # ====== Diagnóstico final
        decision = "Inconclusivo"
        explanation = "Análise geral sugere cautela."

        if hero_stack <= 15 and hero_action == "all-in":
            decision = "👍 Decisão correta"
            explanation = "All-in com stack curto é coerente na estratégia push/fold."
        elif in_open_range and hero_action == "raise":
            decision = "👍 Decisão correta"
            explanation = "Raise com mão dentro do range é ok."
        elif not in_open_range and hero_action == "raise":
            decision = "⚠️ Ação agressiva fora do range sugerido."
            explanation = "Avalie se a jogada não é loose demais."
        elif hero_action == "call" and hero_position in ["UTG", "UTG+1", "MP"]:
            decision = "⚠️ Jogada questionável"
            explanation = "Call fora de posição com stack médio/grande pode ser fraco."

        # ====== Monta texto final
        analysis_text = f"""
🧩 ANÁLISE LOCAL — Poker Replay

📌 Posição: {hero_position}
📌 Cartas: {hero_cards}
📌 Ação: {hero_action}
📌 Stack: {hero_stack} BB
📌 Pote: {pot_size}

➡️ STACK: {stack_cat}
➡️ RANGE: {range_comment}
➡️ POSIÇÃO/AÇÃO: {position_action_comment}

✅ DIAGNÓSTICO: {decision}
💡 EXPLICAÇÃO: {explanation}

Sugestão:
- Respeite ranges por posição e stack.
- Prefira agressividade em posições finais.
- Ajuste ranges conforme o cenário do torneio.
        """.strip()

        return analysis_text
