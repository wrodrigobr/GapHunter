import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RiropoOriginalParserService, RiropoHand, RiropoPlayer, RiropoAction, RiropoStreet } from '../../services/riropo-original-parser.service';

@Component({
  selector: 'app-poker-replayer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './poker-replayer.component.html',
  styleUrls: ['./poker-replayer.component.scss']
})
export class PokerReplayerComponent implements OnInit, OnChanges {
  @Input() handHistory: string = '';
  @Input() backendData: any = null;
  @Input() autoPlay: boolean = false;
  @Input() speed: number = 1;
  @Output() handComplete = new EventEmitter<any>();

  // Parsed hand data
  parsedHand: RiropoHand | null = null;
  
  // Current state
  currentStreetIndex: number = 0;
  currentActionIndex: number = -1;
  isPlaying: boolean = false;
  
  // Display state
  currentPlayers: RiropoPlayer[] = [];
  currentBoard: string[] = [];
  currentPot: number = 0;
  currentBets: { [playerName: string]: number } = {};
  
  // Animation state
  isAnimating: boolean = false;
  lastAction: RiropoAction | null = null;

  constructor(private riropoParser: RiropoOriginalParserService) {}

  ngOnInit() {
    this.initializeReplayer();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['handHistory'] || changes['backendData']) {
      this.initializeReplayer();
    }
  }

  initializeReplayer() {
    console.log('🔍 DEBUG: Inicializando replayer...');
    console.log('🔍 DEBUG: handHistory:', this.handHistory);
    console.log('🔍 DEBUG: backendData:', this.backendData);
    
    if (this.handHistory) {
      // Parse hand history text
      console.log('🔍 DEBUG: Fazendo parse do hand history...');
      this.parsedHand = this.riropoParser.parseHandHistory(this.handHistory);
      console.log('🔍 DEBUG: parsedHand resultado:', this.parsedHand);
    } else if (this.backendData) {
      // Use backend data directly
      console.log('🔍 DEBUG: Convertendo dados do backend...');
      this.parsedHand = this.convertBackendData(this.backendData);
      console.log('🔍 DEBUG: parsedHand convertido:', this.parsedHand);
    }

    if (this.parsedHand) {
      console.log('🔍 DEBUG: Jogadores encontrados:', this.parsedHand.players?.length);
      console.log('🔍 DEBUG: Streets encontradas:', this.parsedHand.streets?.length);
      this.resetToStart();
      if (this.autoPlay) {
        this.startAutoPlay();
      }
    } else {
      console.error('❌ DEBUG: parsedHand é null!');
    }
  }

  convertBackendData(backendData: any): RiropoHand {
    // Convert our backend format to RIROPO format
    return {
      id: backendData.hand_id?.toString() || '0',
      site: 'PokerStars',
      gameType: 'Tournament',
      stakes: backendData.level || 'Unknown',
      tableName: backendData.table_name || 'Unknown',
      maxSeats: 9,
      buttonSeat: 1,
      players: backendData.players?.map((p: any, index: number) => ({
        seat: index + 1,
        name: p.name,
        stack: p.stack,
        isButton: p.is_button,
        isSmallBlind: p.is_small_blind,
        isBigBlind: p.is_big_blind,
        isHero: p.is_hero,
        cards: p.cards,
        position: this.getPositionName(index, backendData.players?.length || 9)
      })) || [],
      blinds: backendData.blinds || { small: 0, big: 0 },
      heroCards: backendData.hero_cards,
      streets: backendData.streets?.map((s: any) => ({
        name: s.name,
        cards: s.cards || [],
        actions: s.actions?.map((a: any) => ({
          player: a.player,
          action: a.action,
          amount: a.amount,
          totalBet: a.total_bet || a.amount
        })) || []
      })) || [],
      summary: {
        totalPot: 0,
        rake: 0
      }
    };
  }

  getPositionName(index: number, totalPlayers: number): string {
    const positions = ['UTG', 'UTG+1', 'MP', 'MP+1', 'CO', 'BTN', 'SB', 'BB'];
    if (totalPlayers <= positions.length) {
      return positions[index] || `P${index + 1}`;
    }
    return `P${index + 1}`;
  }

  resetToStart() {
    if (!this.parsedHand) {
      console.error('❌ DEBUG: resetToStart chamado sem parsedHand!');
      return;
    }

    console.log('🔍 DEBUG: Resetando para início...');
    console.log('🔍 DEBUG: parsedHand.players:', this.parsedHand.players);
    console.log('🔍 DEBUG: parsedHand.heroCards:', this.parsedHand.heroCards);
    
    this.currentStreetIndex = 0;
    this.currentActionIndex = -1;
    
    // Ordenar jogadores por seat para posicionamento correto
    this.currentPlayers = [...this.parsedHand.players].sort((a, b) => a.seat - b.seat);
    
    // Verificar se herói tem cartas
    this.currentPlayers.forEach(player => {
      if (player.isHero) {
        console.log('🔍 DEBUG: Herói encontrado:', player.name);
        console.log('🔍 DEBUG: Cartas do herói no player:', player.cards);
        if (this.parsedHand!.heroCards) {
          player.cards = this.parsedHand!.heroCards;
          console.log('🔍 DEBUG: Cartas do herói definidas:', player.cards);
        }
      }
    });
    
    this.currentBoard = [];
    this.currentPot = 0;
    this.currentBets = {};
    this.lastAction = null;
    this.isPlaying = false;

    console.log('🔍 DEBUG: currentPlayers após reset (ordenados):', this.currentPlayers);
    console.log('🔍 DEBUG: currentPlayers.length:', this.currentPlayers.length);

    // Apply blinds
    this.applyBlinds();
    this.updateDisplay();
  }

  applyBlinds() {
    if (!this.parsedHand) return;

    console.log('🔍 DEBUG: Aplicando blinds...');
    console.log('🔍 DEBUG: Blinds:', this.parsedHand.blinds);

    this.currentPlayers.forEach(player => {
      if (player.isSmallBlind && this.parsedHand!.blinds.small > 0) {
        this.currentBets[player.name] = this.parsedHand!.blinds.small;
        player.stack -= this.parsedHand!.blinds.small;
        this.currentPot += this.parsedHand!.blinds.small;
        console.log('🔍 DEBUG: SB aplicado:', player.name, this.parsedHand!.blinds.small);
      }
      if (player.isBigBlind && this.parsedHand!.blinds.big > 0) {
        this.currentBets[player.name] = this.parsedHand!.blinds.big;
        player.stack -= this.parsedHand!.blinds.big;
        this.currentPot += this.parsedHand!.blinds.big;
        console.log('🔍 DEBUG: BB aplicado:', player.name, this.parsedHand!.blinds.big);
      }
      if (this.parsedHand!.blinds.ante && this.parsedHand!.blinds.ante > 0) {
        this.currentBets[player.name] = (this.currentBets[player.name] || 0) + this.parsedHand!.blinds.ante;
        player.stack -= this.parsedHand!.blinds.ante;
        this.currentPot += this.parsedHand!.blinds.ante;
        console.log('🔍 DEBUG: Ante aplicado:', player.name, this.parsedHand!.blinds.ante);
      }
    });

    console.log('🔍 DEBUG: Pot após blinds:', this.currentPot);
    console.log('🔍 DEBUG: Bets após blinds:', this.currentBets);
  }

  nextAction() {
    if (!this.parsedHand || this.isAnimating) return;

    const currentStreet = this.parsedHand.streets[this.currentStreetIndex];
    if (!currentStreet) return;

    // Check if we can advance within current street
    if (this.currentActionIndex < currentStreet.actions.length - 1) {
      this.currentActionIndex++;
      const action = currentStreet.actions[this.currentActionIndex];
      this.applyAction(action);
    }
    // Move to next street
    else if (this.currentStreetIndex < this.parsedHand.streets.length - 1) {
      this.nextStreet();
    }
    // Hand is complete
    else {
      this.completeHand();
    }

    this.updateDisplay();
  }

  previousAction() {
    if (!this.parsedHand || this.isAnimating) return;

    // Check if we can go back within current street
    if (this.currentActionIndex > -1) {
      this.currentActionIndex--;
    }
    // Move to previous street
    else if (this.currentStreetIndex > 0) {
      this.previousStreet();
    }

    this.rebuildState();
    this.updateDisplay();
  }

  nextStreet() {
    if (!this.parsedHand) return;

    if (this.currentStreetIndex < this.parsedHand.streets.length - 1) {
      // Clear current bets (they go to pot)
      this.clearBetsToNewStreet();
      
      this.currentStreetIndex++;
      this.currentActionIndex = -1;
      
      // Update board cards
      const newStreet = this.parsedHand.streets[this.currentStreetIndex];
      if (newStreet.cards) {
        this.currentBoard = [...newStreet.cards];
      }
    }
  }

  previousStreet() {
    if (!this.parsedHand) return;

    if (this.currentStreetIndex > 0) {
      this.currentStreetIndex--;
      const previousStreet = this.parsedHand.streets[this.currentStreetIndex];
      this.currentActionIndex = previousStreet.actions.length - 1;
    }
  }

  clearBetsToNewStreet() {
    // Move all current bets to pot (already counted, just clear bets)
    this.currentBets = {};
  }

  applyAction(action: RiropoAction) {
    if (!action) return;

    console.log('🔍 DEBUG: Aplicando ação:', action);
    
    this.isAnimating = true;
    this.lastAction = action;

    const player = this.currentPlayers.find(p => p.name === action.player);
    if (!player) {
      console.error('❌ DEBUG: Jogador não encontrado:', action.player);
      return;
    }

    switch (action.action) {
      case 'fold':
        // Player folds, no money changes
        break;
        
      case 'check':
        // Player checks, no money changes
        break;
        
      case 'call':
        if (action.amount > 0) {
          const currentBet = this.currentBets[player.name] || 0;
          const additionalBet = action.amount;
          
          this.currentBets[player.name] = currentBet + additionalBet;
          player.stack -= additionalBet;
          this.currentPot += additionalBet;
          
          console.log('🔍 DEBUG: Call - Pot incrementado:', additionalBet, 'Total pot:', this.currentPot);
        }
        break;
        
      case 'bet':
      case 'raise':
        if (action.amount > 0) {
          const currentBet = this.currentBets[player.name] || 0;
          const additionalBet = action.amount;
          
          this.currentBets[player.name] = currentBet + additionalBet;
          player.stack -= additionalBet;
          this.currentPot += additionalBet;
          
          console.log('🔍 DEBUG: Bet/Raise - Pot incrementado:', additionalBet, 'Total pot:', this.currentPot);
        }
        break;
        
      default:
        // Handle other actions (blinds, antes, etc.)
        if (action.amount > 0) {
          const currentBet = this.currentBets[player.name] || 0;
          const additionalBet = action.amount;
          
          this.currentBets[player.name] = currentBet + additionalBet;
          player.stack -= additionalBet;
          this.currentPot += additionalBet;
          
          console.log('🔍 DEBUG: Ação genérica - Pot incrementado:', additionalBet, 'Total pot:', this.currentPot);
        }
        break;
    }

    // Clear animation after delay
    setTimeout(() => {
      this.isAnimating = false;
    }, 500);
  }

  rebuildState() {
    if (!this.parsedHand) return;

    // Reset to initial state
    this.currentPlayers = [...this.parsedHand.players];
    this.currentBoard = [];
    this.currentPot = 0;
    this.currentBets = {};

    // Apply blinds
    this.applyBlinds();

    // Replay all actions up to current point
    for (let streetIndex = 0; streetIndex <= this.currentStreetIndex; streetIndex++) {
      const street = this.parsedHand.streets[streetIndex];
      if (!street) continue;

      // Update board for this street
      if (street.cards) {
        this.currentBoard = [...street.cards];
      }

      // Apply actions
      const maxActionIndex = streetIndex === this.currentStreetIndex ? 
        this.currentActionIndex : street.actions.length - 1;

      for (let actionIndex = 0; actionIndex <= maxActionIndex; actionIndex++) {
        const action = street.actions[actionIndex];
        if (action) {
          this.applyAction(action);
        }
      }

      // Clear bets between streets (except current street)
      if (streetIndex < this.currentStreetIndex) {
        this.clearBetsToNewStreet();
      }
    }
  }

  updateDisplay() {
    console.log('🔍 DEBUG: updateDisplay chamado');
    console.log('🔍 DEBUG: currentBoard:', this.currentBoard);
    console.log('🔍 DEBUG: currentPot:', this.currentPot);
    console.log('🔍 DEBUG: currentBets:', this.currentBets);
    
    // Update board cards based on current street
    if (this.parsedHand && this.currentStreetIndex >= 0) {
      const currentStreet = this.parsedHand.streets[this.currentStreetIndex];
      if (currentStreet && currentStreet.cards) {
        this.currentBoard = [...currentStreet.cards];
        console.log('🔍 DEBUG: Board atualizado para street', this.currentStreetIndex, ':', this.currentBoard);
      }
    }
    
    // Force change detection
    this.currentPlayers = [...this.currentPlayers];
  }

  startAutoPlay() {
    if (this.isPlaying) return;
    
    this.isPlaying = true;
    this.autoPlayInterval();
  }

  stopAutoPlay() {
    this.isPlaying = false;
  }

  autoPlayInterval() {
    if (!this.isPlaying) return;

    this.nextAction();

    if (this.isHandComplete()) {
      this.stopAutoPlay();
      return;
    }

    setTimeout(() => {
      this.autoPlayInterval();
    }, 1000 / this.speed);
  }

  completeHand() {
    this.stopAutoPlay();
    this.handComplete.emit(this.parsedHand);
  }

  isHandComplete(): boolean {
    if (!this.parsedHand) return true;
    
    const lastStreetIndex = this.parsedHand.streets.length - 1;
    const lastStreet = this.parsedHand.streets[lastStreetIndex];
    
    return this.currentStreetIndex === lastStreetIndex && 
           this.currentActionIndex === lastStreet.actions.length - 1;
  }

  canGoNext(): boolean {
    return !this.isHandComplete();
  }

  canGoPrevious(): boolean {
    return this.currentStreetIndex > 0 || this.currentActionIndex > -1;
  }

  getCurrentStreet(): string {
    if (!this.parsedHand) return 'preflop';
    const street = this.parsedHand.streets[this.currentStreetIndex];
    return street ? street.name : 'preflop';
  }

  getCurrentAction(): RiropoAction | null {
    if (!this.parsedHand) return null;
    const street = this.parsedHand.streets[this.currentStreetIndex];
    if (!street || this.currentActionIndex < 0) return null;
    return street.actions[this.currentActionIndex] || null;
  }

  getPlayerBet(playerName: string): number {
    return this.currentBets[playerName] || 0;
  }

  formatCards(cards: string[]): string {
    if (!cards || cards.length === 0) return '';
    return cards.map(card => this.formatCard(card)).join(' ');
  }

  formatCard(card: string): string {
    if (!card || card.length < 2) return card;
    
    const rank = card.slice(0, -1);
    const suit = card.slice(-1).toLowerCase();
    
    const suitSymbols: { [key: string]: string } = {
      'h': '♥️',
      'd': '♦️',
      'c': '♣️',
      's': '♠️'
    };
    
    return rank + (suitSymbols[suit] || suit);
  }

  getCardClass(card: string): string {
    if (!card || card.length < 2) return '';
    
    const suit = card.slice(-1).toLowerCase();
    return (suit === 'h' || suit === 'd') ? 'red-suit' : 'black-suit';
  }

  getPlayerPosition(player: RiropoPlayer): string {
    return `seat-${player.seat}`;
  }

  getActionDescription(action: RiropoAction): string {
    const actionMap: { [key: string]: string } = {
      'fold': 'desiste',
      'call': 'iguala',
      'raise': 'aumenta',
      'bet': 'aposta',
      'check': 'passa'
    };
    
    const actionText = actionMap[action.action] || action.action;
    
    if (action.amount && action.amount > 0) {
      return `${actionText} ${action.amount}`;
    }
    
    return actionText;
  }

  getProgressPercentage(): number {
    if (!this.parsedHand) return 0;
    
    let totalActions = 0;
    let currentActions = 0;
    
    for (let i = 0; i < this.parsedHand.streets.length; i++) {
      const street = this.parsedHand.streets[i];
      totalActions += street.actions.length;
      
      if (i < this.currentStreetIndex) {
        currentActions += street.actions.length;
      } else if (i === this.currentStreetIndex) {
        currentActions += Math.max(0, this.currentActionIndex + 1);
      }
    }
    
    return totalActions > 0 ? (currentActions / totalActions) * 100 : 0;
  }

  Array = Array; // Para usar no template
  Math = Math; // Para usar no template
}

