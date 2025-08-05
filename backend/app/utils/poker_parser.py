import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PokerStarsParser:
    def __init__(self):
        # Patterns for PokerStars in English
        self.hand_pattern = r"PokerStars Hand #(\d+):"
        self.tournament_pattern = r"Tournament #(\d+),"
        self.table_pattern = r"Table '([^']+)'"
        self.date_pattern = r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
        self.seat_pattern = r"Seat (\d+): ([^(]+) \((\d+) in chips\)"
        self.hole_cards_pattern = r"Dealt to ([^[]+) \[([^\]]+)\]"
        self.action_pattern = r"([^:]+): (folds|calls|raises|bets|checks|all-in)"
        self.pot_pattern = r"Total pot (\d+)"
        self.board_pattern = r"Board \[([^\]]+)\]"
        self.button_pattern = r"Seat #(\d+) is the button"

    def parse_file(self, content: str) -> List[Dict]:
        logger.info(f"Iniciando parse de arquivo com {len(content)} caracteres")
        hands = []
        hand_blocks = self._split_hands(content)
        logger.info(f"Encontrados {len(hand_blocks)} blocos de mãos")

        for i, hand_block in enumerate(hand_blocks):
            logger.info(f"Processando mão {i+1}/{len(hand_blocks)}")
            parsed_hand = self._parse_single_hand(hand_block)
            if parsed_hand:
                hands.append(parsed_hand)
                logger.info(f"Mão {i+1} OK - Hand ID: {parsed_hand.get('hand_id')}")
            else:
                logger.warning(f"Mão {i+1} rejeitada")
        logger.info(f"Parse concluído: {len(hands)} mãos válidas de {len(hand_blocks)} blocos")
        return hands

    def _split_hands(self, content: str) -> List[str]:
        hands = re.split(r'\*{10,}[^*]*\*{10,}', content)
        return [h.strip() for h in hands if h.strip() and 'PokerStars Hand' in h]

    def _parse_single_hand(self, hand_text: str) -> Optional[Dict]:
        try:
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
                'hero_stack': None,
                'pot_size': self._extract_pot_size(hand_text),
                'bet_amount': None,
                'board_cards': self._extract_board_cards(hand_text)
            }

            hero_info = self._extract_hero_info(hand_text)
            if hero_info:
                hand_data.update(hero_info)

            if not hand_data['hand_id']:
                return None

            return hand_data
        except Exception as e:
            logger.error(f"Erro ao processar mão: {e}")
            return None

    def _extract_hand_id(self, text: str) -> Optional[str]:
        match = re.search(self.hand_pattern, text)
        return match.group(1) if match else None

    def _extract_tournament_id(self, text: str) -> Optional[str]:
        match = re.search(self.tournament_pattern, text)
        return match.group(1) if match else None

    def _extract_table_name(self, text: str) -> Optional[str]:
        match = re.search(self.table_pattern, text)
        return match.group(1) if match else None

    def _extract_date(self, text: str) -> Optional[datetime]:
        match = re.search(self.date_pattern, text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S")
            except:
                return None
        return None

    def _extract_pot_size(self, text: str) -> Optional[float]:
        match = re.search(self.pot_pattern, text)
        return float(match.group(1)) if match else None

    def _extract_board_cards(self, text: str) -> Optional[str]:
        match = re.search(self.board_pattern, text)
        return match.group(1) if match else None

    def _extract_hero_info(self, text: str) -> Dict:
        hero_info = {
            'hero_name': None,
            'hero_cards': None,
            'hero_position': None,
            'hero_action': None,
            'hero_stack': None
        }

        hole_cards_match = re.search(self.hole_cards_pattern, text)
        if hole_cards_match:
            hero_name = hole_cards_match.group(1).strip()
            hero_info['hero_name'] = hero_name
            hero_info['hero_cards'] = hole_cards_match.group(2)
            hero_info['hero_position'] = self._find_hero_position(text, hero_name)
            hero_info['hero_action'] = self._find_hero_action(text, hero_name)
            hero_info['hero_stack'] = self._find_hero_stack(text, hero_name)

        return hero_info

    def _find_hero_stack(self, text: str, hero_name: str) -> Optional[float]:
        pattern = rf"Seat \d+: {re.escape(hero_name)} \((\d+) in chips\)"
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                return None
        return None

    def _find_hero_position(self, text: str, hero_name: str) -> Optional[str]:
        button_match = re.search(self.button_pattern, text)
        if not button_match:
            return "EP"
        button_seat = int(button_match.group(1))
        hero_seat_match = re.search(rf"Seat (\d+): {re.escape(hero_name)}", text)
        if not hero_seat_match:
            return "EP"
        hero_seat = int(hero_seat_match.group(1))
        if hero_seat == button_seat:
            return "BTN"
        elif (hero_seat == button_seat + 1) or (button_seat == 9 and hero_seat == 1):
            return "SB"
        elif (hero_seat == button_seat + 2) or (button_seat >= 8 and hero_seat <= 2):
            return "BB"
        elif hero_seat in [button_seat - 1, button_seat - 2] or (button_seat <= 2 and hero_seat >= 8):
            return "LP"
        else:
            return "EP"

    def _find_hero_action(self, text: str, hero_name: str) -> Optional[str]:
        action_patterns = [
            rf"{re.escape(hero_name)}: folds",
            rf"{re.escape(hero_name)}: checks",
            rf"{re.escape(hero_name)}: calls",
            rf"{re.escape(hero_name)}: raises",
            rf"{re.escape(hero_name)}: bets"
        ]
        last_action = None
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if "folds" in pattern:
                    last_action = "fold"
                elif "checks" in pattern:
                    last_action = "check"
                elif "calls" in pattern:
                    last_action = "call"
                elif "raises" in pattern:
                    last_action = "raise"
                elif "bets" in pattern:
                    last_action = "bet"
        return last_action
