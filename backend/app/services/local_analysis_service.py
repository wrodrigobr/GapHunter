from typing import Dict, Any

class LocalAnalysisService:
    def __init__(self):
        pass

    async def analyze_hand_locally(self, hand_data: Dict[str, Any]) -> str:
        """Realiza uma análise local básica da mão de poker."""
        hero_position = hand_data.get("hero_position", "Desconhecida")
        hero_cards = hand_data.get("hero_cards", "Não identificadas")
        hero_action = hand_data.get("hero_action", "Não identificada")
        hero_stack = hand_data.get("hero_stack", "Não identificado")
        pot_size = hand_data.get("pot_size", "Não identificado")

        analysis_text = f"""
ANÁLISE LOCAL:

Posição do Herói: {hero_position}
Cartas do Herói: {hero_cards}
Ação do Herói: {hero_action}
Stack do Herói: {hero_stack}
Tamanho do Pote: {pot_size}

Esta é uma análise básica baseada nos dados extraídos da mão. Para uma análise mais profunda, consulte a análise da IA.

RECOMENDAÇÕES GERAIS (Análise ABC/GTO Simplificada):
- Considere a posição: Jogar mais tight em posições iniciais e mais loose em posições finais.
- Avalie o stack: Com stacks curtos, jogue mais push/fold. Com stacks profundos, explore mais pós-flop.
- Tamanho do pote: Ajuste suas apostas e calls com base no tamanho do pote e nas odds.
- Ranges de mãos: Jogue ranges de mãos apropriados para cada posição e situação.

"""
        return analysis_text


