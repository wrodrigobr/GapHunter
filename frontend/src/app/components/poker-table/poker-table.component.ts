import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

interface PlayerInfo {
  name: string;
  position: number;  // Mudado de string para number
  stack: number;
  cards?: string;    // Tornado opcional
  is_hero: boolean;
  is_button: boolean;
  is_small_blind: boolean;
  is_big_blind: boolean;
  current_bet?: number;
  is_active?: boolean;
  is_folded?: boolean;
}

interface PlayerAction {
  player: string;     // Mudado de player_name para player
  action: string;     // Mudado de action_type para action
  amount: number;
  total_bet: number;  // Adicionado
  timestamp: number;  // Adicionado
}

interface GameStreet {
  name: string;
  cards: string[];    // Mudado de board_cards string para cards array
  actions: PlayerAction[];
}

interface HandReplay {
  hand_id: string;
  tournament_id: string;
  table_name: string;
  level: string;      // Adicionado
  blinds: {           // Mudado de campos separados para objeto
    small: number;
    big: number;
    ante: number;
  };
  players: PlayerInfo[];
  streets: GameStreet[];
  hero_name: string;
  hero_cards: string[];  // Mudado de string para array
}

@Component({
  selector: 'app-poker-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './poker-table.component.html',
  styleUrls: ['./poker-table.component.scss']
})
export class PokerTableComponent implements OnInit, OnChanges {
  @Input() handReplay: HandReplay | null = null;
  @Input() currentStreetIndex: number = 0;
  @Input() currentActionIndex: number = 0;

  // Estado atual da mesa
  currentPlayers: PlayerInfo[] = [];
  currentBoardCards: string[] = [];
  currentPot: number = 0;
  currentStreet: string = 'preflop';
  isFullscreen: boolean = false;
  
  // Posições na mesa (coordenadas para 9 jogadores)
  seatPositions = [
    { x: 50, y: 85 },   // Seat 1 - Bottom center
    { x: 15, y: 70 },   // Seat 2 - Bottom left
    { x: 5, y: 40 },    // Seat 3 - Middle left
    { x: 15, y: 15 },   // Seat 4 - Top left
    { x: 50, y: 5 },    // Seat 5 - Top center
    { x: 85, y: 15 },   // Seat 6 - Top right
    { x: 95, y: 40 },   // Seat 7 - Middle right
    { x: 85, y: 70 },   // Seat 8 - Bottom right
    { x: 65, y: 85 }    // Seat 9 - Bottom right center
  ];

  ngOnInit() {
    this.initializeTable();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['handReplay'] || changes['currentStreetIndex'] || changes['currentActionIndex']) {
      this.updateTableState();
    }
  }

  initializeTable() {
    if (!this.handReplay) return;
    
    // Inicializar jogadores
    this.currentPlayers = this.handReplay.players.map(player => ({
      ...player,
      current_bet: 0,
      is_active: true,
      is_folded: false
    }));

    this.updateTableState();
  }

  updateTableState() {
    if (!this.handReplay) return;

    // Resetar estado dos jogadores
    this.currentPlayers.forEach(player => {
      player.current_bet = 0;
      player.is_active = false;
      player.is_folded = false;
    });

    // Aplicar blinds se estivermos no preflop
    if (this.currentStreetIndex === 0) {
      this.applyBlinds();
    }

    // Aplicar ações até o ponto atual
    this.applyActionsUpToCurrentPoint();

    // Atualizar board cards
    this.updateBoardCards();

    // Atualizar pot
    this.updatePot();
  }

  applyBlinds() {
    if (!this.handReplay) return;

    this.currentPlayers.forEach(player => {
      if (player.is_small_blind) {
        player.current_bet = this.handReplay!.blinds.small;
      } else if (player.is_big_blind) {
        player.current_bet = this.handReplay!.blinds.big;
      }
    });
  }

  applyActionsUpToCurrentPoint() {
    if (!this.handReplay) return;

    // Aplicar ações de todas as streets até a atual
    for (let streetIndex = 0; streetIndex <= this.currentStreetIndex; streetIndex++) {
      const street = this.handReplay.streets[streetIndex];
      if (!street) continue;

      const maxActionIndex = streetIndex === this.currentStreetIndex ? 
        this.currentActionIndex : street.actions.length - 1;

      for (let actionIndex = 0; actionIndex <= maxActionIndex; actionIndex++) {
        const action = street.actions[actionIndex];
        if (!action) continue;

        this.applyAction(action);
      }
    }
  }

  applyAction(action: PlayerAction) {
    const player = this.currentPlayers.find(p => p.name === action.player);
    if (!player) return;

    // Marcar jogador como ativo
    player.is_active = true;

    switch (action.action) {
      case 'fold':
        player.is_folded = true;
        player.is_active = false;
        break;
      case 'call':
        player.current_bet = action.amount;
        break;
      case 'raise':
      case 'bet':
        player.current_bet = action.amount;
        break;
      case 'check':
        // Não altera aposta
        break;
      case 'all-in':
        player.current_bet = action.amount;
        player.stack = 0;
        break;
    }
  }

  updateBoardCards() {
    if (!this.handReplay) return;

    this.currentBoardCards = [];
    
    // Lógica correta para mostrar cartas por street
    for (let i = 0; i <= this.currentStreetIndex; i++) {
      const street = this.handReplay.streets[i];
      if (street && street.cards && street.cards.length > 0) {
        // Para preflop, não há cartas comunitárias
        if (street.name === 'preflop') {
          continue;
        }
        // Para flop, mostrar 3 cartas
        else if (street.name === 'flop') {
          this.currentBoardCards = [...street.cards]; // Substitui, não adiciona
        }
        // Para turn, adicionar apenas 1 carta ao flop
        else if (street.name === 'turn') {
          // Se já temos o flop, adicionar apenas a carta do turn
          if (this.currentBoardCards.length === 3) {
            this.currentBoardCards.push(...street.cards);
          } else {
            // Se não temos flop ainda, pegar flop + turn
            const flopStreet = this.handReplay.streets.find(s => s.name === 'flop');
            if (flopStreet && flopStreet.cards) {
              this.currentBoardCards = [...flopStreet.cards, ...street.cards];
            }
          }
        }
        // Para river, adicionar apenas 1 carta ao turn
        else if (street.name === 'river') {
          // Se já temos flop + turn, adicionar apenas a carta do river
          if (this.currentBoardCards.length === 4) {
            this.currentBoardCards.push(...street.cards);
          } else {
            // Se não temos todas as cartas, construir sequência completa
            const flopStreet = this.handReplay.streets.find(s => s.name === 'flop');
            const turnStreet = this.handReplay.streets.find(s => s.name === 'turn');
            
            let allCards: string[] = [];
            if (flopStreet && flopStreet.cards) allCards.push(...flopStreet.cards);
            if (turnStreet && turnStreet.cards) allCards.push(...turnStreet.cards);
            allCards.push(...street.cards);
            
            this.currentBoardCards = allCards;
          }
        }
      }
    }
  }

  updatePot() {
    if (!this.handReplay) return;

    // Calcular pot baseado nas apostas atuais
    this.currentPot = this.currentPlayers.reduce((total, player) => {
      return total + (player.current_bet || 0);
    }, 0);

    // Adicionar blinds e ante
    this.currentPot += this.handReplay.blinds.small + this.handReplay.blinds.big;
    if (this.handReplay.blinds.ante > 0) {
      this.currentPot += this.handReplay.blinds.ante * this.currentPlayers.length;
    }
  }

  getPlayerPosition(seat: number): { x: number, y: number } {
    return this.seatPositions[seat - 1] || { x: 50, y: 50 };
  }

  getPlayerPositionName(playerNameOrSeat: string | number): any {
    if (typeof playerNameOrSeat === 'string') {
      // Buscar posição por nome do jogador
      const player = this.currentPlayers.find(p => p.name === playerNameOrSeat);
      return player ? this.getPositionName(player.position) : 'Desconhecida';
    } else {
      // Retornar coordenadas por seat number
      return this.seatPositions[playerNameOrSeat - 1] || { x: 50, y: 50 };
    }
  }

  formatCards(cards: string): string {
    if (!cards) return '';
    
    return cards.replace(/([AKQJT98765432])([shdc])/g, (match, rank, suit) => {
      const suitIcons: { [key: string]: string } = {
        's': '♠',
        'h': '♥',
        'd': '♦',
        'c': '♣'
      };
      
      return rank + suitIcons[suit];
    });
  }

  getCardClass(card: string): string {
    if (!card) return '';
    
    const suit = card.slice(-1);
    if (suit === 'h' || suit === 'd') {
      return 'red-suit';
    }
    return 'black-suit';
  }

  formatStack(stack: number): string {
    if (stack >= 1000000) {
      return (stack / 1000000).toFixed(1) + 'M';
    } else if (stack >= 1000) {
      return (stack / 1000).toFixed(1) + 'K';
    }
    return stack.toString();
  }

  getPlayerCardClass(player: PlayerInfo): string {
    let classes = 'player-cards';
    
    if (player.is_hero) {
      classes += ' hero-cards';
    }
    
    if (player.is_folded) {
      classes += ' folded-cards';
    }
    
    return classes;
  }

  getPlayerClass(player: PlayerInfo): string {
    let classes = 'player';
    
    if (player.is_hero) {
      classes += ' hero';
    }
    
    if (player.is_active) {
      classes += ' active';
    }
    
    if (player.is_folded) {
      classes += ' folded';
    }
    
    if (player.is_button) {
      classes += ' button';
    }
    
    return classes;
  }

  getCurrentAction(): PlayerAction | null {
    if (!this.handReplay) return null;
    
    const currentStreet = this.handReplay.streets[this.currentStreetIndex];
    if (!currentStreet) return null;
    
    return currentStreet.actions[this.currentActionIndex] || null;
  }

  getActionDescription(action: PlayerAction): string {
    const actionMap: { [key: string]: string } = {
      'fold': 'desiste',
      'call': 'iguala',
      'raise': 'aumenta',
      'bet': 'aposta',
      'check': 'passa',
      'all-in': 'all-in'
    };
    
    const actionText = actionMap[action.action] || action.action;
    
    if (action.amount > 0) {
      return `${actionText} ${action.amount}`;
    }
    
    return actionText;
  }

  // Métodos de navegação temporal
  previousAction() {
    if (this.canGoPrevious()) {
      if (this.currentActionIndex > 0) {
        this.currentActionIndex--;
      } else if (this.currentStreetIndex > 0) {
        this.currentStreetIndex--;
        const previousStreet = this.handReplay?.streets[this.currentStreetIndex];
        this.currentActionIndex = previousStreet ? previousStreet.actions.length - 1 : 0;
      }
      this.updateTableState();
    }
  }

  nextAction() {
    if (this.canGoNext()) {
      const currentStreet = this.handReplay?.streets[this.currentStreetIndex];
      if (currentStreet && this.currentActionIndex < currentStreet.actions.length - 1) {
        this.currentActionIndex++;
      } else if (this.currentStreetIndex < (this.handReplay?.streets.length || 0) - 1) {
        this.currentStreetIndex++;
        this.currentActionIndex = 0;
      }
      this.updateTableState();
    }
  }

  previousStreet() {
    if (this.canGoPreviousStreet()) {
      this.currentStreetIndex--;
      this.currentActionIndex = 0;
      this.updateTableState();
    }
  }

  nextStreet() {
    if (this.canGoNextStreet()) {
      this.currentStreetIndex++;
      this.currentActionIndex = 0;
      this.updateTableState();
    }
  }

  resetToStart() {
    this.currentStreetIndex = 0;
    this.currentActionIndex = 0;
    this.updateTableState();
  }

  // Métodos de verificação de navegação
  canGoPrevious(): boolean {
    return this.currentStreetIndex > 0 || this.currentActionIndex > 0;
  }

  canGoNext(): boolean {
    if (!this.handReplay) return false;
    
    const currentStreet = this.handReplay.streets[this.currentStreetIndex];
    const isLastStreet = this.currentStreetIndex === this.handReplay.streets.length - 1;
    const isLastAction = currentStreet ? this.currentActionIndex === currentStreet.actions.length - 1 : true;
    
    return !(isLastStreet && isLastAction);
  }

  canGoPreviousStreet(): boolean {
    return this.currentStreetIndex > 0;
  }

  canGoNextStreet(): boolean {
    if (!this.handReplay) return false;
    return this.currentStreetIndex < this.handReplay.streets.length - 1;
  }

  // Métodos auxiliares para o template
  shouldShowCards(player: PlayerInfo): boolean {
    const isHero = Boolean(player.is_hero);
    const isFolded = Boolean(player.is_folded);
    const hasCards = Boolean(player.cards && player.cards.length > 0);
    
    return isHero || (!isFolded && hasCards);
  }

  isNewCard(cardIndex: number): boolean {
    // Lógica para determinar se é uma carta nova (para animação)
    const streetCardCounts = { preflop: 0, flop: 3, turn: 4, river: 5 };
    const currentStreetName = this.handReplay?.streets[this.currentStreetIndex]?.name || 'preflop';
    const expectedCards = streetCardCounts[currentStreetName as keyof typeof streetCardCounts] || 0;
    
    return cardIndex === expectedCards - 1;
  }

  getEmptyCards(): any[] {
    const maxCards = 5;
    const currentCards = this.currentBoardCards.length;
    return new Array(Math.max(0, maxCards - currentCards));
  }

  getTotalActionsInStreet(): number {
    const currentStreet = this.handReplay?.streets[this.currentStreetIndex];
    return currentStreet ? currentStreet.actions.length : 0;
  }

  getProgressPercentage(): number {
    if (!this.handReplay) return 0;
    
    let totalActions = 0;
    let completedActions = 0;
    
    // Contar todas as ações
    this.handReplay.streets.forEach((street, streetIndex) => {
      totalActions += street.actions.length;
      
      if (streetIndex < this.currentStreetIndex) {
        completedActions += street.actions.length;
      } else if (streetIndex === this.currentStreetIndex) {
        completedActions += this.currentActionIndex + 1;
      }
    });
    
    return totalActions > 0 ? (completedActions / totalActions) * 100 : 0;
  }

  getProgressText(): string {
    if (!this.handReplay) return '';
    
    let totalActions = 0;
    let completedActions = 0;
    
    this.handReplay.streets.forEach((street, streetIndex) => {
      totalActions += street.actions.length;
      
      if (streetIndex < this.currentStreetIndex) {
        completedActions += street.actions.length;
      } else if (streetIndex === this.currentStreetIndex) {
        completedActions += this.currentActionIndex + 1;
      }
    });
    
    return `${completedActions} de ${totalActions} ações`;
  }

  getPositionName(seat: number): string {
    if (!this.handReplay) return 'Desconhecida';
    
    // Encontrar o botão
    const buttonPlayer = this.currentPlayers.find(p => p.is_button);
    if (!buttonPlayer) return 'Desconhecida';
    
    const totalPlayers = this.currentPlayers.length;
    const buttonSeat = buttonPlayer.position;
    
    // Calcular posição relativa ao botão
    let relativePosition = (seat - buttonSeat + totalPlayers) % totalPlayers;
    
    const positionNames: { [key: number]: string } = {
      0: 'BTN',
      1: 'SB',
      2: 'BB',
      3: 'UTG',
      4: 'UTG+1',
      5: 'MP',
      6: 'MP+1',
      7: 'CO',
      8: 'HJ'
    };
    
    return positionNames[relativePosition] || `Pos${relativePosition + 1}`;
  }

  // Método para abrir mesa em tela cheia
  openFullscreen() {
    this.isFullscreen = true;
    // Adicionar classe ao body para esconder scroll
    document.body.classList.add('fullscreen-mode');
  }

  closeFullscreen() {
    this.isFullscreen = false;
    // Remover classe do body
    document.body.classList.remove('fullscreen-mode');
  }

  canGoNextStreet(): boolean {
    if (!this.handReplay) return false;
    return this.currentStreetIndex < this.handReplay.streets.length - 1;
  }

  restartHand() {
    this.currentStreetIndex = 0;
    this.currentActionIndex = 0;
    this.updateTableState();
  }
}