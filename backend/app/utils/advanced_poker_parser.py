"""
Parser avançado de hand history para reprodução passo a passo das mãos
Extrai todas as ações sequenciais, posições dos jogadores, cartas comunitárias, etc.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Player:
    """Representa um jogador na mesa"""
    name: str
    position: int  # 1-9 na mesa
    stack: int
    is_hero: bool = False
    is_button: bool = False
    is_small_blind: bool = False
    is_big_blind: bool = False

@dataclass
class Action:
    """Representa uma ação de um jogador"""
    player: str
    action_type: str  # 'fold', 'call', 'raise', 'bet', 'check', 'all-in'
    amount: float = 0.0
    total_bet: float = 0.0  # Total apostado na street
    street: str = 'preflop'  # 'preflop', 'flop', 'turn', 'river'
    timestamp: int = 0  # Ordem sequencial da ação

@dataclass
class Street:
    """Representa uma street (preflop, flop, turn, river)"""
    name: str
    cards: List[str] = None  # Cartas comunitárias
    pot_size: float = 0.0
    actions: List[Action] = None
    
    def __post_init__(self):
        if self.cards is None:
            self.cards = []
        if self.actions is None:
            self.actions = []

@dataclass
class HandReplay:
    """Estrutura completa para reprodução da mão"""
    hand_id: str
    tournament_id: str
    table_name: str
    date_played: datetime
    level: str
    blinds: Dict[str, int]  # {'small': 40, 'big': 80, 'ante': 10}
    
    # Jogadores
    players: List[Player]
    hero_name: str
    hero_cards: List[str]
    
    # Streets
    streets: List[Street]
    
    # Resultado
    winner: str = None
    winning_hand: str = None
    pot_total: float = 0.0
    
    # Análise
    ai_analysis: str = None
    gaps_identified: List[str] = None
    
    def __post_init__(self):
        if self.gaps_identified is None:
            self.gaps_identified = []

class AdvancedPokerParser:
    """Parser avançado para extrair todas as informações da mão"""
    
    def __init__(self):
        # Padrões regex para extração
        self.patterns = {
            'hand_header': r'Mão PokerStars #(\d+): Torneio #(\d+), .+ - Nível ([IVX]+) \((\d+)/(\d+)\) - (.+)',
            'table_info': r"Mesa '([^']+)' (\d+)-max Lugar #(\d+) é o botão",
            'player_seat': r'Lugar (\d+): ([^(]+) \((\d+) em fichas\)',
            'ante': r'([^:]+): coloca ante (\d+)',
            'blind': r'([^:]+): paga o (small|big) blind (\d+)',
            'hero_cards': r'([^:]+) recebe \[([^\]]+)\]',
            'action': r'([^:]+): (desiste|passa|iguala|aumenta|aposta|está all-in)(?:\s+(\d+))?(?:\s+para\s+(\d+))?',
            'flop': r'\*\*\* FLOP \*\*\* \[([^\]]+)\]',
            'turn': r'\*\*\* TURN \*\*\* \[([^\]]+)\] \[([^\]]+)\]',
            'river': r'\*\*\* RIVER \*\*\* \[([^\]]+)\] \[([^\]]+)\]',
            'showdown': r'([^:]+): mostra \[([^\]]+)\] e (ganhou|perdeu)',
            'pot_summary': r'Total pote (\d+)',
        }
        
        # Mapeamento de ações em português
        self.action_mapping = {
            'desiste': 'fold',
            'passa': 'check',
            'iguala': 'call',
            'aumenta': 'raise',
            'aposta': 'bet',
            'está all-in': 'all-in'
        }
        
        # Posições relativas ao botão
        self.position_names = {
            0: 'BTN',    # Botão
            1: 'SB',     # Small Blind
            2: 'BB',     # Big Blind
            3: 'UTG',    # Under The Gun
            4: 'UTG+1',  # UTG+1
            5: 'MP',     # Middle Position
            6: 'MP+1',   # Middle Position+1
            7: 'CO',     # Cut-off
            8: 'HJ'      # Hijack
        }
    
    def parse_hand_for_replay(self, hand_text: str) -> Optional[HandReplay]:
        """
        Parse completo de uma mão para reprodução passo a passo
        """
        try:
            lines = hand_text.strip().split('\n')
            
            # Extrair informações básicas
            hand_info = self._extract_hand_info(lines)
            if not hand_info:
                return None
            
            # Extrair jogadores
            players = self._extract_players(lines)
            if not players:
                return None
            
            # Identificar herói
            hero_name, hero_cards = self._extract_hero_info(lines)
            if not hero_name:
                return None
            
            # Marcar herói nos jogadores
            for player in players:
                if player.name == hero_name:
                    player.is_hero = True
                    break
            
            # Extrair ações por street
            streets = self._extract_streets_and_actions(lines, players)
            
            # Criar objeto HandReplay
            hand_replay = HandReplay(
                hand_id=hand_info['hand_id'],
                tournament_id=hand_info['tournament_id'],
                table_name=hand_info['table_name'],
                date_played=hand_info['date_played'],
                level=hand_info['level'],
                blinds=hand_info['blinds'],
                players=players,
                hero_name=hero_name,
                hero_cards=self._parse_cards(hero_cards),
                streets=streets
            )
            
            return hand_replay
            
        except Exception as e:
            print(f"❌ Erro no parse avançado: {e}")
            return None
    
    def _extract_hand_info(self, lines: List[str]) -> Optional[Dict]:
        """Extrai informações básicas da mão"""
        for line in lines:
            match = re.search(self.patterns['hand_header'], line)
            if match:
                hand_id, tournament_id, level, small_blind, big_blind, date_str = match.groups()
                
                # Parse da data
                try:
                    date_played = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S ET')
                except:
                    date_played = datetime.now()
                
                # Extrair informações da mesa
                table_name = None
                button_position = None
                for table_line in lines:
                    table_match = re.search(self.patterns['table_info'], table_line)
                    if table_match:
                        table_name = table_match.group(1)
                        button_position = int(table_match.group(3))
                        break
                
                return {
                    'hand_id': hand_id,
                    'tournament_id': tournament_id,
                    'table_name': table_name,
                    'date_played': date_played,
                    'level': level,
                    'blinds': {
                        'small': int(small_blind),
                        'big': int(big_blind),
                        'ante': 0  # Será extraído se presente
                    },
                    'button_position': button_position
                }
        
        return None
    
    def _extract_players(self, lines: List[str]) -> List[Player]:
        """Extrai informações dos jogadores"""
        players = []
        button_position = None
        
        # Encontrar posição do botão
        for line in lines:
            table_match = re.search(self.patterns['table_info'], line)
            if table_match:
                button_position = int(table_match.group(3))
                break
        
        # Extrair jogadores
        for line in lines:
            match = re.search(self.patterns['player_seat'], line)
            if match:
                position = int(match.group(1))
                name = match.group(2).strip()
                stack = int(match.group(3))
                
                player = Player(
                    name=name,
                    position=position,
                    stack=stack,
                    is_button=(position == button_position)
                )
                
                players.append(player)
        
        # Ordenar por posição
        players.sort(key=lambda p: p.position)
        
        # Marcar blinds (assumindo estrutura padrão)
        if button_position and len(players) >= 2:
            for i, player in enumerate(players):
                if player.position == button_position:
                    # Small blind é a próxima posição
                    next_idx = (i + 1) % len(players)
                    players[next_idx].is_small_blind = True
                    
                    # Big blind é a posição seguinte
                    bb_idx = (i + 2) % len(players)
                    players[bb_idx].is_big_blind = True
                    break
        
        return players
    
    def _extract_hero_info(self, lines: List[str]) -> tuple:
        """Extrai nome do herói e suas cartas"""
        for line in lines:
            match = re.search(self.patterns['hero_cards'], line)
            if match:
                hero_name = match.group(1).strip()
                hero_cards = match.group(2)
                return hero_name, hero_cards
        
        return None, None
    
    def _extract_streets_and_actions(self, lines: List[str], players: List[Player]) -> List[Street]:
        """Extrai todas as streets e ações"""
        streets = []
        current_street = Street(name='preflop')
        action_counter = 0
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar início de nova street
            if '*** FLOP ***' in line:
                streets.append(current_street)
                flop_match = re.search(self.patterns['flop'], line)
                current_street = Street(
                    name='flop',
                    cards=self._parse_cards(flop_match.group(1)) if flop_match else []
                )
            elif '*** TURN ***' in line:
                streets.append(current_street)
                turn_match = re.search(self.patterns['turn'], line)
                if turn_match:
                    # Apenas a carta do turn (segunda parte do match)
                    turn_card = self._parse_cards(turn_match.group(2))
                    current_street = Street(
                        name='turn',
                        cards=turn_card
                    )
            elif '*** RIVER ***' in line:
                streets.append(current_street)
                river_match = re.search(self.patterns['river'], line)
                if river_match:
                    # Apenas a carta do river (segunda parte do match)
                    river_card = self._parse_cards(river_match.group(2))
                    current_street = Street(
                        name='river',
                        cards=river_card
                    )
            elif '*** SUMÁRIO ***' in line:
                streets.append(current_street)
                break
            
            # Extrair antes
            ante_match = re.search(self.patterns['ante'], line)
            if ante_match:
                player_name = ante_match.group(1).strip()
                ante_amount = int(ante_match.group(2))
                
                action = Action(
                    player=player_name,
                    action_type='ante',
                    amount=ante_amount,
                    total_bet=ante_amount,
                    street=current_street.name,
                    timestamp=action_counter
                )
                
                current_street.actions.append(action)
                action_counter += 1
            
            # Extrair blinds
            blind_match = re.search(self.patterns['blind'], line)
            if blind_match:
                player_name = blind_match.group(1).strip()
                blind_type = blind_match.group(2)  # 'small' ou 'big'
                blind_amount = int(blind_match.group(3))
                
                action = Action(
                    player=player_name,
                    action_type=f'{blind_type}_blind',
                    amount=blind_amount,
                    total_bet=blind_amount,
                    street=current_street.name,
                    timestamp=action_counter
                )
                
                current_street.actions.append(action)
                action_counter += 1
            
            # Extrair ações
            action_match = re.search(self.patterns['action'], line)
            if action_match:
                player_name = action_match.group(1).strip()
                action_pt = action_match.group(2)
                amount = int(action_match.group(3)) if action_match.group(3) else 0
                total_bet = int(action_match.group(4)) if action_match.group(4) else amount
                
                action = Action(
                    player=player_name,
                    action_type=self.action_mapping.get(action_pt, action_pt),
                    amount=amount,
                    total_bet=total_bet,
                    street=current_street.name,
                    timestamp=action_counter
                )
                
                current_street.actions.append(action)
                action_counter += 1
            
            i += 1
        
        # Adicionar última street se não foi adicionada
        if current_street and current_street not in streets:
            streets.append(current_street)
        
        return streets
    
    def _parse_cards(self, cards_str: str) -> List[str]:
        """Parse de cartas (ex: 'As Kh' -> ['As', 'Kh'])"""
        if not cards_str:
            return []
        
        # Remover espaços extras e dividir
        cards = cards_str.strip().split()
        return [card.strip() for card in cards if card.strip()]
    
    def get_action_sequence(self, hand_replay: HandReplay) -> List[Dict]:
        """
        Retorna sequência completa de ações para reprodução
        """
        sequence = []
        
        # Adicionar setup inicial
        sequence.append({
            'type': 'setup',
            'players': [
                {
                    'name': p.name,
                    'position': p.position,
                    'stack': p.stack,
                    'is_hero': p.is_hero,
                    'is_button': p.is_button,
                    'is_sb': p.is_small_blind,
                    'is_bb': p.is_big_blind
                }
                for p in hand_replay.players
            ],
            'blinds': hand_replay.blinds,
            'hero_cards': hand_replay.hero_cards
        })
        
        # Adicionar ações por street
        for street in hand_replay.streets:
            # Adicionar cartas comunitárias se houver
            if street.cards:
                sequence.append({
                    'type': 'community_cards',
                    'street': street.name,
                    'cards': street.cards
                })
            
            # Adicionar ações
            for action in street.actions:
                sequence.append({
                    'type': 'action',
                    'street': street.name,
                    'player': action.player,
                    'action': action.action_type,
                    'amount': action.amount,
                    'total_bet': action.total_bet,
                    'timestamp': action.timestamp
                })
        
        return sequence
    
    def analyze_hand_for_gaps(self, hand_replay: HandReplay) -> List[str]:
        """
        Análise básica para identificar possíveis gaps
        """
        gaps = []
        
        # Verificar ações do herói
        hero_actions = []
        for street in hand_replay.streets:
            for action in street.actions:
                if action.player == hand_replay.hero_name:
                    hero_actions.append(action)
        
        # Análises básicas de gaps
        for action in hero_actions:
            # Gap: fold com cartas premium
            if action.action_type == 'fold' and action.street == 'preflop':
                hero_cards = hand_replay.hero_cards
                if len(hero_cards) == 2:
                    # Verificar se são cartas premium (simplificado)
                    ranks = [card[0] for card in hero_cards]
                    if 'A' in ranks or 'K' in ranks:
                        gaps.append(f"Possível gap: fold com cartas premium ({' '.join(hero_cards)}) no preflop")
            
            # Gap: call sem odds adequadas (análise simplificada)
            if action.action_type == 'call' and action.amount > 0:
                gaps.append(f"Revisar: call de {action.amount} no {action.street}")
        
        return gaps

# Função de conveniência para uso nos endpoints
def parse_hand_for_table_replay(hand_text: str) -> Optional[Dict]:
    """
    Parse de mão para reprodução na mesa virtual
    Retorna estrutura simplificada para o frontend
    """
    parser = AdvancedPokerParser()
    hand_replay = parser.parse_hand_for_replay(hand_text)
    
    if not hand_replay:
        return None
    
    # Converter para estrutura JSON-friendly
    return {
        'hand_id': hand_replay.hand_id,
        'tournament_id': hand_replay.tournament_id,
        'table_name': hand_replay.table_name,
        'level': hand_replay.level,
        'blinds': hand_replay.blinds,
        'players': [
            {
                'name': p.name,
                'position': p.position,
                'stack': p.stack,
                'is_hero': p.is_hero,
                'is_button': p.is_button,
                'is_sb': p.is_small_blind,
                'is_bb': p.is_big_blind
            }
            for p in hand_replay.players
        ],
        'hero_name': hand_replay.hero_name,
        'hero_cards': hand_replay.hero_cards,
        'streets': [
            {
                'name': s.name,
                'cards': s.cards,
                'actions': [
                    {
                        'player': a.player,
                        'action': a.action_type,
                        'amount': a.amount,
                        'total_bet': a.total_bet,
                        'timestamp': a.timestamp
                    }
                    for a in s.actions
                ]
            }
            for s in hand_replay.streets
        ],
        'action_sequence': parser.get_action_sequence(hand_replay),
        'gaps_identified': parser.analyze_hand_for_gaps(hand_replay)
    }

