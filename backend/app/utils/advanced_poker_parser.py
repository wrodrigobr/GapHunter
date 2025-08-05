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
    cards: str = "" # Adicionado para armazenar cartas do showdown

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
        # Padrões regex para extração em inglês
        self.patterns = {
            'hand_header': r'PokerStars Hand #(\d+): Tournament #(\d+), .+ - Level ([IVX]+) \((\d+)/(\d+)\) - (.+)',
            'table_info': r"Table '([^']+)' (\d+)-max Seat #(\d+) is the button",
            'player_seat': r'Seat (\d+): ([^(]+) \((\d+) in chips\)',
            'ante': r'([^:]+): posts the ante (\d+)',
            'blind': r'([^:]+): posts (small|big) blind (\d+)',
            'hero_cards': r'Dealt to ([^[]+) \[([^\]]+)\]',
            'action': r'([^:]+): (folds|calls|raises|bets|checks|all-in)(?:\s+(\d+))?(?:\s+to\s+(\d+))?',
            'flop': r'\*\*\* FLOP \*\*\* \[([^\]]+)\]',
            'turn': r'\*\*\* TURN \*\*\* \[([^\]]+)\] \[([^\]]+)\]',
            'river': r'\*\*\* RIVER \*\*\* \[([^\]]+)\] \[([^\]]+)\]',
            'showdown': r'([^:]+): shows \[([^\]]+)\]',
            'pot_summary': r'Total pot (\d+)',
        }
        
        # Mapeamento de ações em inglês
        self.action_mapping = {
            'folds': 'fold',
            'checks': 'check',
            'calls': 'call',
            'raises': 'raise',
            'bets': 'bet',
            'all-in': 'all-in'
        }
        
        # Mapeamento de posições
        self.position_mapping = {
            1: 'UTG',   # Under the Gun
            2: 'UTG+1', # Under the Gun +1
            3: 'MP',    # Middle Position
            4: 'MP+1',  # Middle Position +1
            5: 'CO',    # Cutoff
            6: 'BTN',   # Button
            7: 'SB',    # Small Blind
            8: 'BB',    # Big Blind
            9: 'BB'     # Big Blind (9-max)
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
                
                print(f"🔍 DEBUG: Extraindo hand info da linha: {line.strip()}")
                print(f"🔍 DEBUG: hand_id: {hand_id}")
                print(f"🔍 DEBUG: tournament_id: {tournament_id}")
                print(f"🔍 DEBUG: level: {level}")
                print(f"🔍 DEBUG: small_blind: {small_blind}")
                print(f"🔍 DEBUG: big_blind: {big_blind}")
                print(f"🔍 DEBUG: date_str: {date_str}")
                
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
        
        print(f"🔍 DEBUG: Extraindo jogadores...")
        
        # Encontrar posição do botão
        for line in lines:
            table_match = re.search(self.patterns['table_info'], line)
            if table_match:
                button_position = int(table_match.group(3))
                print(f"🔍 DEBUG: Button encontrado na posição {button_position} da linha: {line.strip()}")
                break
        
        if button_position is None:
            print(f"⚠️  DEBUG: Button não encontrado!")
        
        # Extrair jogadores
        for line in lines:
            match = re.search(self.patterns['player_seat'], line)
            if match:
                position = int(match.group(1))
                name = match.group(2).strip()
                stack = int(match.group(3))
                
                is_button = (position == button_position)
                if is_button:
                    print(f"🔍 DEBUG: Jogador {name} (pos {position}) marcado como button")
                
                player = Player(
                    name=name,
                    position=position,
                    stack=stack,
                    is_button=is_button
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
                    print(f"🔍 DEBUG: Jogador {players[next_idx].name} (pos {players[next_idx].position}) marcado como small blind")
                    
                    # Big blind é a posição seguinte
                    bb_idx = (i + 2) % len(players)
                    players[bb_idx].is_big_blind = True
                    print(f"🔍 DEBUG: Jogador {players[bb_idx].name} (pos {players[bb_idx].position}) marcado como big blind")
                    break
        
        print(f"🔍 DEBUG: Total de jogadores extraídos: {len(players)}")
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
        """Extrai streets e ações do hand history"""
        streets = []
        current_street = None
        
        print(f"🔍 DEBUG: Processando {len(lines)} linhas para extrair streets e ações")
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            print(f"🔍 DEBUG: Linha {i}: '{line}'")
            
            # Detectar início de nova street
            if '*** HOLE CARDS ***' in line:
                if current_street:
                    streets.append(current_street)
                current_street = Street(name='preflop')
                print(f"🔍 DEBUG: Iniciando street: preflop")
                
            elif '*** FLOP ***' in line:
                if current_street:
                    streets.append(current_street)
                print(f"🔍 FLOP: '{line}'")
                if '[' in line and ']' in line:
                    start_idx = line.find('[')
                    end_idx = line.find(']')
                    if start_idx != -1 and end_idx != -1:
                        cards_str = line[start_idx + 1:end_idx]
                        parsed_cards = self._parse_cards(cards_str)
                        print(f"✅ FLOP cards: {parsed_cards}")
                        current_street = Street(name='flop', cards=parsed_cards)
                    else:
                        current_street = Street(name='flop', cards=[])
                else:
                    current_street = Street(name='flop', cards=[])
                print(f"🔍 DEBUG: Street mudou para: flop")
                    
            elif '*** TURN ***' in line:
                if current_street:
                    streets.append(current_street)
                print(f"🔍 TURN: '{line}'")
                if '[' in line and ']' in line:
                    # Encontrar o segundo par de colchetes (carta do turn)
                    bracket_count = 0
                    start_idx = -1
                    end_idx = -1
                    
                    for j, char in enumerate(line):
                        if char == '[':
                            bracket_count += 1
                            if bracket_count == 2:  # Segundo par de colchetes
                                start_idx = j
                        elif char == ']':
                            if bracket_count == 2:  # Segundo par de colchetes
                                end_idx = j
                                break
                    
                    if start_idx != -1 and end_idx != -1:
                        cards_str = line[start_idx + 1:end_idx]
                        parsed_cards = self._parse_cards(cards_str)
                        print(f"✅ TURN card: {parsed_cards}")
                        current_street = Street(name='turn', cards=parsed_cards)
                    else:
                        current_street = Street(name='turn', cards=[])
                else:
                    current_street = Street(name='turn', cards=[])
                    
            elif '*** RIVER ***' in line:
                if current_street:
                    streets.append(current_street)
                print(f"🔍 RIVER: '{line}'")
                if '[' in line and ']' in line:
                    # Encontrar o segundo par de colchetes (carta do river)
                    bracket_count = 0
                    start_idx = -1
                    end_idx = -1
                    
                    for j, char in enumerate(line):
                        if char == '[':
                            bracket_count += 1
                            if bracket_count == 2:  # Segundo par de colchetes
                                start_idx = j
                        elif char == ']':
                            if bracket_count == 2:  # Segundo par de colchetes
                                end_idx = j
                                break
                    
                    if start_idx != -1 and end_idx != -1:
                        cards_str = line[start_idx + 1:end_idx]
                        parsed_cards = self._parse_cards(cards_str)
                        print(f"✅ RIVER card: {parsed_cards}")
                        current_street = Street(name='river', cards=parsed_cards)
                    else:
                        print(f"⚠️  DEBUG: Não foi possível extrair carta do river da linha: '{line}'")
                        current_street = Street(name='river', cards=[])
                else:
                    print(f"⚠️  DEBUG: River sem colchetes na linha: '{line}'")
                    current_street = Street(name='river', cards=[])
                    
            elif '*** SHOW DOWN ***' in line:
                print(f"🔍 DEBUG: Encontrou SHOW DOWN na linha {i}")
                if current_street:
                    streets.append(current_street)
                # Criar street para showdown
                current_street = Street(name='showdown')
                
                # Log das próximas linhas para debug
                print(f"🔍 DEBUG: Próximas linhas após SHOW DOWN:")
                for j in range(i + 1, min(i + 10, len(lines))):
                    print(f"  Linha {j}: '{lines[j].strip()}'")
                    if lines[j].strip().startswith('*** SUMMARY ***'):
                        break
                
            elif '*** SUMMARY ***' in line:
                print(f"🔍 DEBUG: Encontrou SUMMARY na linha {i}")
                if current_street:
                    streets.append(current_street)
                # Criar street para summary
                current_street = Street(name='summary')
                
                # Processar linhas do summary para extrair informações do vencedor
                i += 1
                while i < len(lines):
                    summary_line = lines[i].strip()
                    if not summary_line or summary_line.startswith('==='):
                        break
                    
                    print(f"🔍 DEBUG: Processando linha do summary: '{summary_line}'")
                    
                    # Extrair informações do vencedor
                    won_match = re.search(r'Seat \d+: ([^(]+) \(.*\) showed \[([^\]]+)\] and won \(([0-9,]+)\)', summary_line)
                    if won_match:
                        player_name = won_match.group(1).strip()
                        cards = won_match.group(2)
                        amount = int(won_match.group(3).replace(',', ''))
                        print(f"🏆 DEBUG: Vencedor encontrado: {player_name} com cartas {cards} ganhou ${amount}")
                        
                        action = Action(
                            player=player_name,
                            action_type='won',
                            amount=amount,
                            total_bet=amount,
                            street='summary',
                            timestamp=0,
                            cards=cards
                        )
                        current_street.actions.append(action)
                    
                    i += 1
                continue
            
            # Processar ações se estamos em uma street
            elif current_street and line and not line.startswith('***'):
                print(f"🔍 DEBUG: Processando linha de ação: '{line}' para street: {current_street.name}")
                print(f"🔍 DEBUG: current_street: {current_street.name}, line: '{line}'")
                
                # Extrair ação
                action = self._parse_action_line(line, current_street.name)
                if action:
                    current_street.actions.append(action)
                    print(f"🔍 DEBUG: Ação adicionada à street '{current_street.name}': {action.player} {action.action_type} ${action.amount}")
                    print(f"🔍 DEBUG: Street atual: {current_street.name}")
                    print(f"🔍 DEBUG: Linha processada: '{line}'")
                else:
                    print(f"⚠️  DEBUG: Falha ao processar linha: '{line}'")
            else:
                print(f"🔍 DEBUG: Linha ignorada: '{line}' (current_street: {current_street.name if current_street else 'None'})")
            
            i += 1
        
        # Adicionar última street se não foi adicionada
        if current_street and current_street not in streets:
            streets.append(current_street)
        
        print(f"🔍 DEBUG: Total de streets extraídas: {len(streets)}")
        for i, street in enumerate(streets):
            print(f"🔍 DEBUG: Street {i+1}: {street.name} - {len(street.cards)} cartas - {len(street.actions)} ações")
            for j, action in enumerate(street.actions):
                cards_info = f" (cartas: {action.cards})" if action.cards else ""
                print(f"      {j+1}. {action.player}: {action.action_type} {action.amount}{cards_info}")
        
        return streets
    
    def _parse_action_line(self, line: str, street_name: str) -> Optional[Action]:
        """Parse uma linha de ação"""
        print(f"🔍 DEBUG: Parseando linha: '{line}' para street: {street_name}")
        
        # Padrões para diferentes tipos de ação
        patterns = {
            'ante': r'^([^:]+): posts the ante ([0-9,]+)',
            'small_blind': r'^([^:]+): posts small blind ([0-9,]+)',
            'big_blind': r'^([^:]+): posts big blind ([0-9,]+)',
            'fold': r'^([^:]+): folds',
            'check': r'^([^:]+): checks',
            'call': r'^([^:]+): calls ([0-9,]+)',
            'bet': r'^([^:]+): bets ([0-9,]+)',
            'raise': r'^([^:]+): raises ([0-9,]+) to ([0-9,]+)',
            'all-in': r'^([^:]+): bets ([0-9,]+) and is all-in',
            'shows': r'^([^:]+): shows \[([^\]]+)\]',
            'mucks': r'^([^:]+): mucks hand',
            'collected': r'^([^:]+) collected ([0-9,]+) from pot'
        }
        
        for action_type, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                player_name = match.group(1).strip()
                amount = 0
                total_bet = 0
                cards = ""
                
                print(f"🔍 DEBUG: Match encontrado para {action_type}: {match.groups()}")
                
                if action_type in ['ante', 'small_blind', 'big_blind', 'call', 'bet', 'all-in']:
                    amount = int(match.group(2).replace(',', ''))
                    total_bet = amount
                elif action_type == 'raise':
                    amount = int(match.group(2).replace(',', ''))
                    total_bet = int(match.group(3).replace(',', ''))
                elif action_type == 'collected':
                    amount = int(match.group(2).replace(',', ''))
                    total_bet = amount
                elif action_type == 'shows':
                    # Extrair cartas do showdown
                    cards = match.group(2)
                    print(f"🔍 DEBUG: Cartas extraídas do showdown para {player_name}: {cards}")
                elif action_type == 'mucks':
                    # Para mucks, não há cartas
                    print(f"🔍 DEBUG: {player_name} mucks hand")
                
                action = Action(
                    player=player_name,
                    action_type=action_type,
                    amount=amount,
                    total_bet=total_bet,
                    street=street_name,
                    timestamp=0,  # Será atualizado depois
                    cards=cards
                )
                
                print(f"🔍 DEBUG: Ação criada: {player_name} {action_type} ${amount} cartas: '{cards}'")
                return action
        
        print(f"⚠️  DEBUG: Nenhum padrão encontrado para linha: '{line}'")
        return None
    
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

