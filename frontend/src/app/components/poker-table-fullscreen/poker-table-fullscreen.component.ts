import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';

interface PlayerInfo {
  name: string;
  position: number;
  stack: number;
  is_hero: boolean;
  is_button: boolean;
  is_small_blind: boolean;
  is_big_blind: boolean;
  cards?: string;
  current_bet?: number;
  is_folded?: boolean;
  is_active?: boolean;
}

interface PlayerAction {
  player: string;
  action: string;
  amount: number;
  total_bet: number;
  timestamp: number;
}

interface Street {
  name: string;
  cards: string[];
  actions: PlayerAction[];
}

interface HandReplay {
  hand_id: string;
  tournament_id: string;
  table_name: string;
  level: string;
  blinds: {
    small: number;
    big: number;
    ante: number;
  };
  players: PlayerInfo[];
  hero_name: string;
  hero_cards: string[];
  streets: Street[];
  action_sequence: any[];
  gaps_identified: string[];
}

@Component({
  selector: 'app-poker-table-fullscreen',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './poker-table-fullscreen.component.html',
  styleUrls: ['./poker-table-fullscreen.component.scss']
})
export class PokerTableFullscreenComponent implements OnInit {
  handReplay: HandReplay | null = null;
  currentStreetIndex: number = 0;
  currentActionIndex: number = 0;
  currentPlayers: PlayerInfo[] = [];
  currentBoardCards: string[] = [];
  currentPot: number = 0;
  currentStreet: string = 'preflop';

  // Posições dos assentos na mesa (em porcentagem)
  seatPositions = [
    { x: 50, y: 85 },  // Seat 1 - Bottom
    { x: 20, y: 70 },  // Seat 2 - Bottom Left
    { x: 10, y: 40 },  // Seat 3 - Left
    { x: 20, y: 15 },  // Seat 4 - Top Left
    { x: 50, y: 5 },   // Seat 5 - Top
    { x: 80, y: 15 },  // Seat 6 - Top Right
    { x: 90, y: 40 },  // Seat 7 - Right
    { x: 80, y: 70 },  // Seat 8 - Bottom Right
    { x: 65, y: 85 }   // Seat 9 - Bottom Right
  ];

  constructor(private route: ActivatedRoute) {}

  ngOnInit() {
    // Recuperar dados da URL
    this.route.queryParams.subscribe(params => {
      if (params['data']) {
        try {
          const fullscreenData = JSON.parse(decodeURIComponent(params['data']));
          this.handReplay = fullscreenData.handReplay;
          this.currentStreetIndex = fullscreenData.currentStreetIndex || 0;
          this.currentActionIndex = fullscreenData.currentActionIndex || 0;
          
          if (this.handReplay) {
            this.initializeReplay();
          }
        } catch (error) {
          console.error('Erro ao carregar dados da mesa:', error);
        }
      }
    });
  }

  initializeReplay() {
    if (!this.handReplay) return;

    // Inicializar jogadores
    this.currentPlayers = this.handReplay.players.map(player => ({
      ...player,
      current_bet: 0,
      is_folded: false,
      is_active: false
    }));

    // Aplicar estado atual
    this.updateGameState();
  }

  updateGameState() {
    if (!this.handReplay) return;

    // Reset estado
    this.currentPlayers.forEach(player => {
      player.current_bet = 0;
      player.is_folded = false;
      player.is_active = false;
    });

    // Aplicar ações até o ponto atual
    for (let streetIndex = 0; streetIndex <= this.currentStreetIndex; streetIndex++) {
      const street = this.handReplay.streets[streetIndex];
      if (!street) continue;

      this.currentStreet = street.name;
      
      const maxActionIndex = streetIndex === this.currentStreetIndex ? 
        this.currentActionIndex : street.actions.length - 1;

      for (let actionIndex = 0; actionIndex <= maxActionIndex; actionIndex++) {
        const action = street.actions[actionIndex];
        if (!action) continue;

        this.applyAction(action);
      }
    }

    this.updateBoardCards();
    this.updatePot();
  }

  applyAction(action: PlayerAction) {
    const player = this.currentPlayers.find(p => p.name === action.player);
    if (!player) return;

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
    
    for (let i = 0; i <= this.currentStreetIndex; i++) {
      const street = this.handReplay.streets[i];
      if (street && street.cards && street.cards.length > 0) {
        if (street.name === 'preflop') {
          continue;
        }
        else if (street.name === 'flop') {
          this.currentBoardCards = [...street.cards];
        }
        else if (street.name === 'turn') {
          if (this.currentBoardCards.length === 3) {
            this.currentBoardCards.push(...street.cards);
          } else {
            const flopStreet = this.handReplay.streets.find(s => s.name === 'flop');
            if (flopStreet && flopStreet.cards) {
              this.currentBoardCards = [...flopStreet.cards, ...street.cards];
            }
          }
        }
        else if (street.name === 'river') {
          if (this.currentBoardCards.length === 4) {
            this.currentBoardCards.push(...street.cards);
          } else {
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

    this.currentPot = this.currentPlayers.reduce((total, player) => {
      return total + (player.current_bet || 0);
    }, 0);

    this.currentPot += this.handReplay.blinds.small + this.handReplay.blinds.big;
    if (this.handReplay.blinds.ante > 0) {
      this.currentPot += this.handReplay.blinds.ante * this.currentPlayers.length;
    }
  }

  // Métodos de navegação
  previousAction() {
    if (this.currentActionIndex > 0) {
      this.currentActionIndex--;
    } else if (this.currentStreetIndex > 0) {
      this.currentStreetIndex--;
      const prevStreet = this.handReplay?.streets[this.currentStreetIndex];
      this.currentActionIndex = prevStreet ? prevStreet.actions.length - 1 : 0;
    }
    this.updateGameState();
  }

  nextAction() {
    if (!this.handReplay) return;
    
    const currentStreet = this.handReplay.streets[this.currentStreetIndex];
    if (!currentStreet) return;

    if (this.currentActionIndex < currentStreet.actions.length - 1) {
      this.currentActionIndex++;
    } else if (this.currentStreetIndex < this.handReplay.streets.length - 1) {
      this.currentStreetIndex++;
      this.currentActionIndex = 0;
    }
    this.updateGameState();
  }

  previousStreet() {
    if (this.currentStreetIndex > 0) {
      this.currentStreetIndex--;
      this.currentActionIndex = 0;
      this.updateGameState();
    }
  }

  nextStreet() {
    if (!this.handReplay) return;
    
    if (this.currentStreetIndex < this.handReplay.streets.length - 1) {
      this.currentStreetIndex++;
      this.currentActionIndex = 0;
      this.updateGameState();
    }
  }

  restart() {
    this.currentStreetIndex = 0;
    this.currentActionIndex = 0;
    this.updateGameState();
  }

  // Métodos auxiliares
  getPlayerPosition(seat: number): { x: number, y: number } {
    return this.seatPositions[seat - 1] || { x: 50, y: 50 };
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
      
      const suitColors: { [key: string]: string } = {
        's': '#000000',
        'h': '#ff0000',
        'd': '#ff0000',
        'c': '#000000'
      };
      
      const suitIcon = suitIcons[suit];
      const suitColor = suitColors[suit];
      
      return `${rank}<span style="color: ${suitColor}">${suitIcon}</span>`;
    });
  }

  formatStack(stack: number): string {
    if (stack >= 1000000) {
      return (stack / 1000000).toFixed(1) + 'M';
    } else if (stack >= 1000) {
      return (stack / 1000).toFixed(1) + 'K';
    }
    return stack.toString();
  }

  shouldShowCards(player: PlayerInfo): boolean {
    const isHero = Boolean(player.is_hero);
    const isFolded = Boolean(player.is_folded);
    const hasCards = Boolean(player.cards && player.cards.length > 0);
    
    return isHero || (!isFolded && hasCards);
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
    
    return classes;
  }

  closeFullscreen() {
    window.close();
  }
}

