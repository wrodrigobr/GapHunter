import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PokerStarsParser:
    def __init__(self):
        # Padrões para PokerStars em português
        self.hand_pattern = r"Mão PokerStars #(\d+):"
        self.tournament_pattern = r"Torneio #(\d+),"
        self.table_pattern = r"Mesa '([^']+)'"
        self.date_pattern = r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
        self.seat_pattern = r"Lugar (\d+): ([^(]+) \((\d+) em fichas\)"
        self.hole_cards_pattern = r"(\w+) recebe \[([^\]]+)\]"
        self.action_pattern = r"([^:]+): (desiste|passa|iguala|aumenta|aposta|está all-in)"
        self.pot_pattern = r"Total pote (\d+)"
        self.board_pattern = r"Mesa \[([^\]]+)\]"
        self.button_pattern = r"Lugar #(\d+) é o botão"
        self.hero_stack_pattern = r"^Lugar \d+: {hero_name} \((\d+) em fichas\)"

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
        # O formato usa asteriscos para separar as mãos
        hands = re.split(r'\*{10,}[^*]*\*{10,}', content)
        
        # Filtrar blocos vazios e muito pequenos
        valid_hands = []
        for hand in hands:
            hand = hand.strip()
            if hand and len(hand) > 50 and 'Mão PokerStars' in hand:
                valid_hands.append(hand)
        
        logger.info(f"Divisão de mãos: {len(valid_hands)} blocos válidos de {len(hands)} total")
        return valid_hands

    def _parse_single_hand(self, hand_text: str) -> Optional[Dict]:
        """Parse uma única mão de poker"""
        try:
            logger.debug(f"Parsing hand text (primeiros 200 chars): {hand_text[:200]}")
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
                'hero_stack': None, # Será preenchido por _extract_hero_info
                'pot_size': self._extract_pot_size(hand_text),
                'bet_amount': None,
                'board_cards': self._extract_board_cards(hand_text)
            }
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
        
        # Procurar por "recebe" para identificar o herói (formato português)
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
        # Procurar pela linha que define o botão
        button_match = re.search(self.button_pattern, text)
        if not button_match:
            return "EP"  # Early position por padrão
        
        button_seat = int(button_match.group(1))
        
        # Encontrar o lugar do herói
        hero_seat_pattern = rf"Lugar (\d+): {re.escape(hero_name)}"
        hero_seat_match = re.search(hero_seat_pattern, text)
        
        if not hero_seat_match:
            return "EP"
        
        hero_seat = int(hero_seat_match.group(1))
        
        # Determinar posição relativa ao botão
        if hero_seat == button_seat:
            return "BTN"
        elif (hero_seat == button_seat + 1) or (button_seat == 9 and hero_seat == 1):
            return "SB"
        elif (hero_seat == button_seat + 2) or (button_seat >= 8 and hero_seat <= 2):
            return "BB"
        elif hero_seat in [button_seat - 1, button_seat - 2] or (button_seat <= 2 and hero_seat >= 8):
            return "LP"  # Late position
        else:
            return "EP"  # Early position

    def _find_hero_action(self, text: str, hero_name: str) -> Optional[str]:
        """Encontra a última ação do herói"""
        # Padrões de ação em português
        action_patterns = [
            rf"{re.escape(hero_name)}: desiste",
            rf"{re.escape(hero_name)}: passa",
            rf"{re.escape(hero_name)}: iguala",
            rf"{re.escape(hero_name)}: aumenta",
            rf"{re.escape(hero_name)}: aposta"
        ]
        
        last_action = None
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if "desiste" in pattern:
                    last_action = "fold"
                elif "passa" in pattern:
                    last_action = "check"
                elif "iguala" in pattern:
                    last_action = "call"
                elif "aumenta" in pattern:
                    last_action = "raise"
                elif "aposta" in pattern:
                    last_action = "bet"
        
        return last_action



    def _extract_hero_stack(self, text: str, hero_name: str) -> Optional[float]:
        """Extrai o stack inicial do herói na mão"""
        if not hero_name:
            return None
        
        # O padrão precisa ser formatado com o nome do herói
        pattern = self.hero_stack_pattern.format(hero_name=re.escape(hero_name))
        match = re.search(pattern, text)
        if match:
            try:
                stack = float(match.group(1))
                logger.debug(f"Stack do herói extraído: {stack}")
                return stack
            except ValueError:
                logger.warning(f"Não foi possível converter o stack para float: {match.group(1)}")
                return None
        logger.debug(f"Stack do herói não encontrado para {hero_name}")
        return None