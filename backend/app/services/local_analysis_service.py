from typing import Dict, Any

class LocalAnalysisService:
    def __init__(self):
        pass

    async def analyze_hand_locally(self, hand_data: Dict[str, Any]) -> str:
        """Análise local mais detalhada."""

        hero_position = hand_data.get("hero_position", "Desconhecida")
        hero_cards = hand_data.get("hero_cards", "Não identificadas")
        hero_action = hand_data.get("hero_action", "Não identificada")
        hero_stack = hand_data.get("hero_stack")
        pot_size = hand_data.get("pot_size")

        # Regra simplificada para stack
        stack_comment = ""
        if hero_stack is not None:
            if hero_stack < 10:
                stack_comment = "Stack curto: situação de push/fold."
            elif hero_stack < 30:
                stack_comment = "Stack médio: é possível abrir mais mãos, mas cuidado com all-ins."
            else:
                stack_comment = "Stack confortável: margem para jogadas pós-flop."

        # Verifica coerência posição x ação
        position_action_comment = ""
        if hero_position.lower() in ["early", "utg", "utg+1"]:
            if hero_action.lower() in ["call", "limp"]:
                position_action_comment = "Jogada passiva em posição inicial pode ser ruim. Prefira abrir raise ou fold."
            elif hero_action.lower() in ["raise"]:
                position_action_comment = "Ação agressiva em posição inicial é ok, desde que o range seja tight."
        elif hero_position.lower() in ["late", "button", "cutoff"]:
            if hero_action.lower() in ["raise"]:
                position_action_comment = "Boa agressividade em posição final."
            elif hero_action.lower() in ["call"]:
                position_action_comment = "Call em posição final é aceitável, mas avalie odds e agressividade."

        # Avalia força pré-flop se possível (super simplificado)
        hand_strength_comment = ""
        if hero_cards != "Não identificadas":
            strong_hands = ["AA", "KK", "QQ", "AK", "JJ", "AQ"]
            if any(strong in hero_cards.replace(" ", "") for strong in strong_hands):
                hand_strength_comment = "Mão forte pré-flop."
            else:
                hand_strength_comment = "Mão de força média/baixa — jogue com cautela."

        # Diagnóstico final (exemplo simples)
        decision_ok = "Inconclusivo"
        explanation = ""

        if "Mão forte" in hand_strength_comment and "raise" in hero_action.lower():
            decision_ok = "Decisão correta"
            explanation = "Ação agressiva com mão forte está de acordo com estratégia."
        elif "Mão de força média" in hand_strength_comment and hero_action.lower() == "call":
            decision_ok = "Aceitável"
            explanation = "Call com mão média pode ser ok, mas depende de posição e tamanho de stack."
        elif "Jogada passiva" in position_action_comment:
            decision_ok = "Questionável"
            explanation = "Jogada passiva fora de posição com mão média geralmente não é lucrativa."

        analysis_text = f"""
ANÁLISE LOCAL DETALHADA

Posição do Herói: {hero_position}
Cartas do Herói: {hero_cards}
Ação do Herói: {hero_action}
Stack do Herói: {hero_stack}
Tamanho do Pote: {pot_size}

👉 STACK: {stack_comment}
👉 POSIÇÃO vs AÇÃO: {position_action_comment}
👉 FORÇA DA MÃO: {hand_strength_comment}

📌 DIAGNÓSTICO: {decision_ok}
💡 EXPLICAÇÃO: {explanation}

RECOMENDAÇÃO GERAL:
- Avalie o range da mão para sua posição.
- Prefira agressividade em posições finais.
- Evite jogadas marginais em posições iniciais.
"""

        return analysis_text