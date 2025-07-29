import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PokerStarsParser:
    def __init__(self):
        # Padrões mais robustos para PokerStars
        self.hand_pattern = r"PokerStars Hand #(\d+):"
        self.tournament_pattern = r"Tournament #(\d+),"
        self.table_pattern = r"Table '([^']+)'"
        self.date_pattern = r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
        self.seat_pattern = r"Seat (\d+): ([^(]+) \((\d+) in chips\)"
        self.hole_cards_pattern = r"Dealt to ([^[]+) \[([^\]]+)\]"
        self.action_pattern = r"([^:]+): (folds|checks|calls|bets|raises|all-in)"
        self.pot_pattern = r"Total pot (\d+)"
        self.board_pattern = r"Board \[([^\]]+)\]"

    def parse_file(self, content: str) -> List[Dict]:
        """Parse um arquivo de hand history e retorna lista de mãos"""
        logger.info(f"Iniciando parse de arquivo com {len(content)} caracteres")
        
        hands = []
        hand_blocks = self._split_hands(content)
        
        logger.info(f"Encontrados {len(hand_blocks)} blocos de mãos")
        
        for i, hand_block in enumerate(hand_blocks):
            logger.info(f"Processando mão {i+1}/{len(hand_blocks)}")
            parsed_hand = self._parse_single_hand(hand_block)
            if parsed_hand:
                hands.append(parsed_hand)
                logger.info(f"Mão {i+1} processada com sucesso - Hand ID: {parsed_hand.get('hand_id')}")
            else:
                logger.warning(f"Falha ao processar mão {i+1}")
        
        logger.info(f"Parse concluído: {len(hands)} mãos válidas de {len(hand_blocks)} blocos")
        return hands

    def _split_hands(self, content: str) -> List[str]:
        """Divide o conteúdo em blocos de mãos individuais"""
        # Tentar diferentes separadores
        separators = [
            r'\n\n\n+',  # Múltiplas linhas vazias
            r'\*{10,}',   # Múltiplos asteriscos
            r'PokerStars Hand #'  # Início de nova mão
        ]
        
        hands = []
        
        # Primeiro tentar por asteriscos (formato comum)
        if '***' in content:
            hands = re.split(r'\*{5,}[^*]*\*{5,}', content)
        else:
            # Tentar por múltiplas quebras de linha
            hands = re.split(r'\n\n\n+', content)
        
        # Filtrar blocos vazios e muito pequenos
        valid_hands = []
        for hand in hands:
            hand = hand.strip()
            if hand and len(hand) > 50 and 'PokerStars Hand' in hand:
                valid_hands.append(hand)
        
        logger.info(f"Divisão de mãos: {len(valid_hands)} blocos válidos de {len(hands)} total")
        return valid_hands

    def _parse_single_hand(self, hand_text: str) -> Optional[Dict]:
        """Parse uma única mão de poker"""
        try:
            logger.debug(f"Parsing hand text (primeiros 200 chars): {hand_text[:200]}...")
            
            hand_data = {
                'raw_hand': hand_text,
                'hand_id': self._extract_hand_id(hand_text),
                'tournament_id': self._extract_tournament_id(hand_text),
                'table_name': self._extract_table_name(hand_text),
                'date_played': self._extract_date(hand_text),
                'hero_name': None,
                'hero_position': None,
                'hero_cards': None,
                'hero_action': None,
                'pot_size': self._extract_pot_size(hand_text),
                'bet_amount': None,
                'board_cards': self._extract_board_cards(hand_text)
            }

            # Log dos dados extraídos
            logger.debug(f"Dados extraídos: hand_id={hand_data['hand_id']}, "
                        f"tournament_id={hand_data['tournament_id']}, "
                        f"table_name={hand_data['table_name']}")

            # Extrair informações do herói
            hero_info = self._extract_hero_info(hand_text)
            if hero_info:
                hand_data.update(hero_info)
                logger.debug(f"Hero info: {hero_info}")

            # Validar dados obrigatórios
            if not hand_data['hand_id']:
                logger.warning("Hand ID não encontrado - mão será rejeitada")
                return None

            return hand_data
        except Exception as e:
            logger.error(f"Erro ao processar mão: {e}")
            logger.debug(f"Texto da mão problemática: {hand_text[:500]}...")
            return None

    def _extract_hand_id(self, text: str) -> Optional[str]:
        match = re.search(self.hand_pattern, text)
        result = match.group(1) if match else None
        logger.debug(f"Hand ID extraído: {result}")
        return result

    def _extract_tournament_id(self, text: str) -> Optional[str]:
        match = re.search(self.tournament_pattern, text)
        result = match.group(1) if match else None
        logger.debug(f"Tournament ID extraído: {result}")
        return result

    def _extract_table_name(self, text: str) -> Optional[str]:
        match = re.search(self.table_pattern, text)
        result = match.group(1) if match else None
        logger.debug(f"Table name extraído: {result}")
        return result

    def _extract_date(self, text: str) -> Optional[datetime]:
        match = re.search(self.date_pattern, text)
        if match:
            try:
                result = datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S")
                logger.debug(f"Data extraída: {result}")
                return result
            except Exception as e:
                logger.warning(f"Erro ao converter data: {e}")
                return None
        logger.debug("Data não encontrada")
        return None

    def _extract_pot_size(self, text: str) -> Optional[float]:
        match = re.search(self.pot_pattern, text)
        result = float(match.group(1)) if match else None
        logger.debug(f"Pot size extraído: {result}")
        return result

    def _extract_board_cards(self, text: str) -> Optional[str]:
        match = re.search(self.board_pattern, text)
        result = match.group(1) if match else None
        logger.debug(f"Board cards extraído: {result}")
        return result

    def _extract_hero_info(self, text: str) -> Dict:
        """Extrai informações do herói (jogador principal)"""
        hero_info = {}
        
        # Procurar por "Dealt to" para identificar o herói
        hole_cards_match = re.search(self.hole_cards_pattern, text)
        if hole_cards_match:
            hero_info['hero_name'] = hole_cards_match.group(1).strip()
            hero_info['hero_cards'] = hole_cards_match.group(2)
            
            # Encontrar posição do herói
            hero_info['hero_position'] = self._find_hero_position(text, hero_info['hero_name'])
            
            # Encontrar última ação do herói
            hero_info['hero_action'] = self._find_hero_action(text, hero_info['hero_name'])

        return hero_info

    def _find_hero_position(self, text: str, hero_name: str) -> Optional[str]:
        """Encontra a posição do herói na mesa"""
        # Implementação simplificada - pode ser melhorada
        if "Button" in text and hero_name in text:
            return "BTN"
        elif "Small Blind" in text and hero_name in text:
            return "SB"
        elif "Big Blind" in text and hero_name in text:
            return "BB"
        else:
            return "EP"  # Early position por padrão

    def _find_hero_action(self, text: str, hero_name: str) -> Optional[str]:
        """Encontra a última ação do herói"""
        actions = re.findall(f"{re.escape(hero_name)}: (\\w+)", text)
        return actions[-1] if actions else None

