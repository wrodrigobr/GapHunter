import httpx
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class AIAnalysisService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = "mistralai/mistral-7b-instruct"

    async def analyze_hand(self, hand_data: Dict) -> Optional[str]:
        """Analisa uma mão de poker usando IA"""
        try:
            prompt = self._build_analysis_prompt(hand_data)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Você é um especialista em poker GTO (Game Theory Optimal) focado em torneios (MTTs). Analise mãos de poker e forneça feedback técnico detalhado."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"Erro na API: {response.status_code} - {response.text}")
                    return self._fallback_analysis(hand_data)
                    
        except Exception as e:
            print(f"Erro ao analisar mão: {e}")
            return self._fallback_analysis(hand_data)

    def _build_analysis_prompt(self, hand_data: Dict) -> str:
        """Constrói o prompt para análise da mão"""
        prompt = f"""
Você é um coach profissional de poker especializado em torneios (MTTs) e estratégia GTO. Analise esta mão de poker e forneça feedback técnico detalhado.

INFORMAÇÕES DA MÃO:
- ID da Mão: {hand_data.get('hand_id', 'N/A')}
- Torneio: {hand_data.get('tournament_id', 'N/A')}
- Mesa: {hand_data.get('table_name', 'N/A')}
- Herói: {hand_data.get('hero_name', 'N/A')}
- Posição: {hand_data.get('hero_position', 'N/A')}
- Cartas do Herói: {hand_data.get('hero_cards', 'N/A')}
- Ação Principal: {hand_data.get('hero_action', 'N/A')}
- Tamanho do Pot: {hand_data.get('pot_size', 'N/A')}
- Board: {hand_data.get('board_cards', 'N/A')}

HAND HISTORY COMPLETA:
{hand_data.get('raw_hand', '')}

ANÁLISE SOLICITADA:

1. **RESUMO DA SITUAÇÃO**
   - Contexto da mão (nível de blinds, stack sizes relativos)
   - Dinâmica da mesa e posicionamento

2. **AVALIAÇÃO DA JOGADA**
   - A ação do herói foi correta? (Escala: Excelente/Boa/Aceitável/Ruim/Terrível)
   - Justificativa técnica baseada em GTO

3. **ANÁLISE TÉCNICA**
   - Range de mãos apropriado para a posição
   - Considerações sobre pot odds e implied odds
   - Leitura de oponentes baseada nas ações

4. **ALTERNATIVAS ESTRATÉGICAS**
   - Outras linhas de jogo possíveis
   - Quando cada alternativa seria preferível

5. **PONTOS DE MELHORIA**
   - Gaps específicos identificados
   - Conceitos para estudar
   - Situações similares para praticar

6. **CONTEXTO DE TORNEIO**
   - Considerações sobre ICM (Independent Chip Model)
   - Ajustes baseados no estágio do torneio
   - Gestão de stack e bubble considerations

Seja específico, educativo e construtivo. Use terminologia técnica apropriada mas mantenha explicações claras.
"""
        return prompt

    def _fallback_analysis(self, hand_data: Dict) -> str:
        """Análise básica quando a IA não está disponível"""
        action = hand_data.get('hero_action', 'unknown')
        position = hand_data.get('hero_position', 'unknown')
        cards = hand_data.get('hero_cards', 'unknown')
        
        return f"""
ANÁLISE BÁSICA (IA indisponível):

Posição: {position}
Cartas: {cards}
Ação: {action}

Esta é uma análise básica. Para análise completa com IA, verifique a configuração da API.

Considerações gerais:
- Em torneios, considere sempre o stack size e blind levels
- Posição é fundamental para tomada de decisões
- Observe os padrões dos oponentes
- Mantenha disciplina com bankroll management

Para análise mais detalhada, configure a integração com OpenRouter.
"""

