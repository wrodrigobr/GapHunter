import { Component, OnInit, OnDestroy, Input, Output, EventEmitter, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { RiropoParserService, RiropoHand, RiropoPlayer, RiropoAction } from '../../services/riropo-parser.service';

@Component({
  selector: 'app-poker-replayer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './poker-replayer.component.html',
  styleUrls: ['./poker-replayer.component.scss']
})
export class PokerReplayerComponent implements OnInit, OnDestroy {
  @Input() handHistory: string = '';
  @Input() autoPlay: boolean = false;
  @Input() speed: number = 1; // 1 = normal, 2 = 2x, 0.5 = 0.5x
  @Input() backendData: any = null; // Dados do backend
  @Output() handComplete = new EventEmitter<RiropoHand>();

  // Expor Array para uso no template
  Array = Array;
  
  // Expor Math para uso no template
  Math = Math;

  currentHand: RiropoHand | null = null;
  currentActionIndex: number = -1;
  isPlaying: boolean = false;
  isPaused: boolean = false;
  currentStreet: string = 'preflop';
  visibleActions: RiropoAction[] = [];
  pot: number = 0;
  board: string[] = [];

  private subscription: Subscription = new Subscription();
  private playInterval: any;

  constructor(
    private riropoService: RiropoParserService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.subscription.add(
      this.riropoService.getCurrentHand().subscribe(hand => {
        this.currentHand = hand;
        if (hand && this.autoPlay) {
          this.startReplay();
        }
      })
    );

    // Se temos dados do backend, usar eles
    if (this.backendData) {
      console.log('🔍 DEBUG: Usando dados do backend:', this.backendData);
      this.loadBackendData(this.backendData);
    } else if (this.handHistory) {
      this.loadHand(this.handHistory);
    }
  }

  /**
   * Load data from backend
   */
  loadBackendData(backendData: any): void {
    console.log('🔍 DEBUG: loadBackendData chamado com:', backendData);
    
    // Converter dados do backend para formato RiropoHand
    const hand: RiropoHand = {
      handId: backendData.hand_id,
      tableName: backendData.table_name,
      gameMode: 'tournament',
      gameType: 'holdem',
      blinds: backendData.blinds,
      buttonSeat: 0, // Será calculado
      players: backendData.players.map((p: any) => ({
        name: p.name,
        seat: p.position,
        stack: p.stack,
        cards: p.is_hero ? (backendData.hero_cards?.join(' ') || '') : (p.cards || ''),
        isButton: p.is_button,
        isSmallBlind: p.is_small_blind,
        isBigBlind: p.is_big_blind,
        isHero: p.is_hero,
        isActive: false,
        isFolded: false,
        currentBet: 0,
        bet: 0,
        isAllIn: false,
        isChecked: false,
        position: `Pos${p.position}`
      })),
      actions: [],
      board: [],
      streets: backendData.streets || [], // Incluir streets do backend
      pot: 0,
      hero: backendData.hero_name,
      heroCards: backendData.hero_cards?.join(' ') || '',
      rawText: ''
    };

    // Converter ações das streets para formato RiropoAction
    const allActions: RiropoAction[] = [];
    let timestamp = 0;
    
    for (const street of backendData.streets || []) {
      for (const action of street.actions) {
        allActions.push({
          player: action.player,
          action: action.action,
          amount: action.amount,
          street: street.name,
          timestamp: timestamp++,
          cards: action.cards || '',
          total_bet: action.total_bet // Adicionar total_bet para o raise
        });
      }
    }
    
    hand.actions = allActions;
    
    // Construir board a partir das streets
    const allBoardCards: string[] = [];
    for (const street of backendData.streets || []) {
      if (street.cards && street.cards.length > 0) {
        allBoardCards.push(...street.cards);
      }
    }
    hand.board = allBoardCards;
    
    this.currentHand = hand;
    console.log('🔍 DEBUG: currentHand criado a partir do backend:', this.currentHand);
    console.log('🔍 DEBUG: Streets disponíveis:', this.currentHand.streets);
    console.log('🔍 DEBUG: Board criado:', this.currentHand.board);
    console.log('🔍 DEBUG: Hero cards:', this.currentHand.heroCards);
    
    this.resetReplay();
    if (this.autoPlay) {
      this.startReplay();
    }
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
    this.stopReplay();
  }

  /**
   * Load and parse hand history
   */
  loadHand(handText: string): void {
    console.log('🔍 DEBUG: loadHand chamado com texto:', handText.substring(0, 200) + '...');
    
    const hand = this.riropoService.parseHandHistory(handText);
    console.log('🔍 DEBUG: Hand parseado:', hand);
    
    if (hand) {
      this.currentHand = hand;
      console.log('🔍 DEBUG: currentHand definido:', this.currentHand);
      console.log('🔍 DEBUG: currentHand.board:', this.currentHand.board);
      console.log('🔍 DEBUG: currentHand.actions:', this.currentHand.actions.length, 'ações');
      
      // Log das primeiras ações para debug
      this.currentHand.actions.slice(0, 5).forEach((action, index) => {
        console.log(`🔍 DEBUG: Ação ${index}:`, action);
      });
      
      this.resetReplay();
      if (this.autoPlay) {
        this.startReplay();
      }
    } else {
      console.error('❌ DEBUG: Falha ao parsear hand');
    }
  }

  /**
   * Start replay
   */
  startReplay(): void {
    console.log('🔍 DEBUG: startReplay chamado');
    console.log('🔍 DEBUG: currentHand existe?ante?', !!this.currentHand);
    console.log('🔍 DEBUG: isPlaying?', this.isPlaying);
    console.log('🔍 DEBUG: isPaused?', this.isPaused);
    console.log('🔍 DEBUG: currentActionIndex antes:', this.currentActionIndex);
    
    if (!this.currentHand || this.isPlaying) {
      console.log('🔍 DEBUG: startReplay - retornando (currentHand não existe ou já está playing)');
      return;
    }

    console.log('🔍 DEBUG: Iniciando replay...');
    this.isPlaying = true;
    this.isPaused = false;
    this.currentActionIndex = -1;
    this.resetBoard();
    this.resetPot();
    this.resetPlayerStates();
    this.processAntes(); // Processar antes no início

    console.log('🔍 DEBUG: startReplay - chamando playNextAction');
    this.playNextAction();
  }

  /**
   * Pause replay
   */
  pauseReplay(): void {
    this.isPaused = true;
    if (this.playInterval) {
      clearTimeout(this.playInterval);
    }
  }

  /**
   * Resume replay
   */
  resumeReplay(): void {
    if (!this.isPlaying || !this.isPaused) return;
    
    this.isPaused = false;
    this.playNextAction();
  }

  /**
   * Stop replay
   */
  stopReplay(): void {
    this.isPlaying = false;
    this.isPaused = false;
    this.currentActionIndex = -1;
    this.resetBoard();
    this.resetPot();
    this.resetPlayerStates();
    this.visibleActions = [];

    if (this.playInterval) {
      clearTimeout(this.playInterval);
    }
  }

  /**
   * Reset replay to beginning
   */
  resetReplay(): void {
    this.stopReplay();
    this.currentActionIndex = -1;
    this.resetBoard();
    this.resetPot();
    this.resetPlayerStates();
    this.visibleActions = [];
    
    // Processar antes se houver
    this.processAntes();
  }

  /**
   * Process antes actions at the beginning
   */
  private processAntes(): void {
    if (!this.currentHand || !this.currentHand.blinds.ante) return;
    
    console.log(`💰 DEBUG: Processando antes para ${this.currentHand.players.length} jogadores`);
    
    this.currentHand.players.forEach(player => {
      // Subtrair ante do stack de cada jogador
      const anteAmount = this.currentHand?.blinds?.ante || 0;
      player.stack -= anteAmount;
      console.log(`💰 DEBUG: ${player.name} pagou ante $${anteAmount}, stack: $${player.stack}`);
    });
  }

  /**
   * Play next action
   */
  private playNextAction(): void {
    if (!this.currentHand || this.currentActionIndex >= this.visibleActions.length - 1) {
      this.completeReplay();
      return;
    }

    this.currentActionIndex++;
    const action = this.visibleActions[this.currentActionIndex];
    
    console.log(`🔍 DEBUG: playNextAction - Processando ação ${this.currentActionIndex}: ${action.player} - ${action.action}`);
    
    // Processar a ação
    this.processAction(action);
    
    // Aguardar antes da próxima ação
    const delay = this.getActionDelay(action);
    setTimeout(() => {
      if (!this.isPaused) {
        this.playNextAction();
      }
    }, delay / this.speed);
  }

  /**
   * Process a single action
   */
  private processAction(action: RiropoAction): void {
    console.log(`🔍 DEBUG: processAction INÍCIO - ${action.player} - ${action.action} - $${action.amount}`);
    console.log(`🔍 DEBUG: processAction - action.street: ${action.street}, currentStreet: ${this.currentStreet}`);
    
    // Update street if needed
    if (action.street !== this.currentStreet) {
      console.log(`🔍 DEBUG: Mudando de street: ${this.currentStreet} -> ${action.street}`);
      this.currentStreet = action.street;
      this.updateBoard();
      this.clearPlayerBets(); // Limpar apostas ao mudar de street
      
      // Se estamos navegando manualmente, parar aqui para mostrar apenas as cartas
      if (!this.isPlaying || this.isPaused) {
        console.log(`🔍 DEBUG: Street mudou para ${action.street} - cartas mostradas, aguardando próxima ação`);
        return; // Não processar a ação ainda
      }
    }

    // Update pot (somar ao pote existente)
    if (action.amount) {
      this.pot += action.amount;
      console.log(`💰 DEBUG: Pote atualizado: $${this.pot} (+$${action.amount})`);
    }

    // Update player state
    this.updatePlayerState(action);
    
    console.log(`🔍 DEBUG: processAction FIM - ${action.player} - ${action.action}`);
  }

  /**
   * Update board cards based on current street
   */
  private updateBoard(): void {
    if (!this.currentHand) return;

    console.log(`🔍 DEBUG: updateBoard - currentStreet: ${this.currentStreet}`);
    console.log(`🔍 DEBUG: updateBoard - currentHand.board:`, this.currentHand.board);

    // Construir board a partir das cartas das streets do backend
    const allBoardCards: string[] = [];
    
    // Procurar por cartas nas streets do backend (se disponível)
    if (this.currentHand.streets) {
      console.log('🔍 DEBUG: Streets disponíveis no currentHand:', this.currentHand.streets);
      
      for (const street of this.currentHand.streets) {
        if (street.cards && street.cards.length > 0) {
          allBoardCards.push(...street.cards);
          console.log(`🔍 DEBUG: Adicionadas cartas da street ${street.name}:`, street.cards);
        }
      }
    } else {
      // Fallback: usar o board do currentHand se disponível
      if (this.currentHand.board && this.currentHand.board.length > 0) {
        allBoardCards.push(...this.currentHand.board);
        console.log(`🔍 DEBUG: Usando board do currentHand:`, this.currentHand.board);
      }
    }

    switch (this.currentStreet) {
      case 'flop':
        this.board = allBoardCards.slice(0, 3);
        console.log(`🔍 DEBUG: updateBoard - flop board:`, this.board);
        break;
      case 'turn':
        this.board = allBoardCards.slice(0, 4);
        console.log(`🔍 DEBUG: updateBoard - turn board:`, this.board);
        break;
      case 'river':
        this.board = allBoardCards.slice(0, 5);
        console.log(`🔍 DEBUG: updateBoard - river board:`, this.board);
        break;
      default:
        this.board = [];
        console.log(`🔍 DEBUG: updateBoard - default board:`, this.board);
    }
  }

  /**
   * Clear player bets when changing street
   */
  private clearPlayerBets(): void {
    if (!this.currentHand) return;

    console.log('🔍 DEBUG: Limpando apostas dos jogadores');
    this.currentHand.players.forEach(player => {
      player.currentBet = 0;
      player.bet = 0;
      // NÃO resetar isChecked aqui para manter o badge de CHECK visível
    });
  }

  /**
   * Update player state based on action
   */
  private updatePlayerState(action: RiropoAction): void {
    if (!this.currentHand) return;

    const player = this.currentHand.players.find(p => p.name === action.player);
    if (!player) {
      console.log(`❌ DEBUG: Jogador não encontrado: ${action.player}`);
      return;
    }

    console.log(`🔍 DEBUG: updatePlayerState - ${action.player}:`);
    console.log(`  - Action: ${action.action}`);
    console.log(`  - Amount: ${action.amount}`);
    console.log(`  - Street: ${action.street}`);
    console.log(`  - Cards: ${action.cards}`);
    console.log(`  - Stack ANTES da ação: $${player.stack}`);
    console.log(`  - isChecked ANTES: ${player.isChecked}`);

    switch (action.action) {
      case 'fold':
        player.isFolded = true;
        player.isActive = false;
        player.bet = 0;
        player.isChecked = false;
        console.log(`❌ DEBUG: ${action.player} desistiu`);
        break;
      case 'call':
        // Calcular quanto o jogador precisa pagar para completar
        const callAmount = action.amount || 0;
        console.log(`🔍 DEBUG: ${action.player} chamando - callAmount: $${callAmount}, bet atual: $${player.bet}, currentBet: $${player.currentBet}`);
        console.log(`🔍 DEBUG: ${action.player} - stack ANTES: $${player.stack}`);
        
        // Somar à aposta anterior (não substituir)
        player.currentBet += callAmount;
        player.bet += callAmount;
        // Subtrair stack quando o jogador chama
        player.stack -= callAmount;
        player.isActive = true;
        player.isAllIn = false;
        player.isChecked = false;
        console.log(`💰 DEBUG: ${action.player} chamou $${callAmount}, aposta total: $${player.bet}, stack DEPOIS: $${player.stack}`);
        break;
      case 'raise':
      case 'bet':
        // Para raise, usar total_bet (já inclui a aposta anterior)
        // Para bet, usar amount (nova aposta)
        const betAmount = action.action === 'raise' ? (action.total_bet || action.amount || 0) : (action.amount || 0);
        // Para raise, substituir a aposta (já inclui o valor anterior)
        // Para bet, substituir a aposta (nova aposta)
        player.currentBet = betAmount;
        player.bet = betAmount;
        // Subtrair stack APENAS do jogador que está apostando
        player.stack -= betAmount;
        player.isActive = true;
        player.isAllIn = false;
        player.isChecked = false;
        console.log(`💰 DEBUG: ${action.player} apostou $${betAmount}, stack DEPOIS: $${player.stack}`);
        break;
      case 'all-in':
        player.currentBet = action.amount || 0;
        player.bet = action.amount || 0;
        // Subtrair stack APENAS do jogador que está apostando
        player.stack -= action.amount || 0;
        player.isActive = true;
        player.isAllIn = true;
        player.isChecked = false;
        console.log(`🔥 DEBUG: ${action.player} ALL-IN $${action.amount}, stack DEPOIS: $${player.stack}`);
        break;
      case 'check':
        player.isActive = true;
        player.bet = 0;
        player.isChecked = true;
        console.log(`✅ DEBUG: ${action.player} deu CHECK (stack NÃO alterado)`);
        console.log(`✅ DEBUG: player.isChecked = ${player.isChecked}`);
        console.log(`✅ DEBUG: player.isActive = ${player.isActive}`);
        console.log(`✅ DEBUG: player.isChecked DEPOIS = ${player.isChecked}`);
        break;
      case 'shows':
        // Jogador mostrou cartas (ganhou ou empatou)
        if (action.cards) {
          player.cards = action.cards;
          console.log(`🃏 DEBUG: ${action.player} mostrou cartas: ${action.cards}`);
        }
        player.isActive = true;
        player.isWinner = true; // Marcar como vencedor
        break;
      case 'collected':
        // Jogador coletou o pote (vencedor)
        if (action.cards) {
          player.cards = action.cards;
          console.log(`🃏 DEBUG: ${action.player} coletou com cartas: ${action.cards}`);
        }
        player.isActive = true;
        player.isWinner = true; // Marcar como vencedor
        console.log(`🏆 DEBUG: ${action.player} GANHOU o pote de $${action.amount}`);
        break;
      case 'won':
        // Jogador ganhou (sinônimo de collected)
        if (action.cards) {
          player.cards = action.cards;
          console.log(`🃏 DEBUG: ${action.player} ganhou com cartas: ${action.cards}`);
        }
        player.isActive = true;
        player.isWinner = true; // Marcar como vencedor
        console.log(`🏆 DEBUG: ${action.player} GANHOU o pote`);
        break;
      case 'mucks':
        // Jogador descartou cartas (perdeu)
        player.cards = ''; // Esconder cartas
        player.isActive = false;
        player.isWinner = false; // Não é vencedor
        console.log(`❌ DEBUG: ${action.player} descartou cartas (perdeu)`);
        break;
    }
  }

  /**
   * Get delay for action based on type
   */
  private getActionDelay(action: RiropoAction): number {
    switch (action.action) {
      case 'fold':
        return 500;
      case 'check':
        return 300;
      case 'call':
        return 800;
      case 'raise':
        return 1000;
      case 'bet':
        return 800;
      case 'all-in':
        return 1200;
      default:
        return 500;
    }
  }

  /**
   * Reset board
   */
  private resetBoard(): void {
    this.board = [];
    this.currentStreet = 'preflop';
  }

  /**
   * Reset pot
   */
  private resetPot(): void {
    if (this.currentHand) {
      // Incluir antes e blinds iniciais
      let initialPot = 0;
      
      // Adicionar antes (se houver)
      if (this.currentHand.blinds.ante) {
        const totalPlayers = this.currentHand.players.length;
        initialPot += this.currentHand.blinds.ante * totalPlayers;
        console.log(`💰 DEBUG: Adicionando antes: ${totalPlayers} jogadores x $${this.currentHand.blinds.ante} = $${initialPot}`);
      }
      
      // Adicionar blinds
      initialPot += this.currentHand.blinds.small + this.currentHand.blinds.big;
      console.log(`💰 DEBUG: Adicionando blinds: SB $${this.currentHand.blinds.small} + BB $${this.currentHand.blinds.big} = $${this.currentHand.blinds.small + this.currentHand.blinds.big}`);
      
      this.pot = initialPot;
      console.log(`💰 DEBUG: Pote inicial: $${this.pot}`);
    } else {
      this.pot = 0;
    }
  }

  /**
   * Reset player states
   */
  private resetPlayerStates(): void {
    if (!this.currentHand) return;

    this.currentHand.players.forEach(player => {
      player.isActive = false;
      player.isFolded = false;
      player.currentBet = 0;
      player.bet = 0; // Resetar bet também
      player.isAllIn = false; // Resetar all-in status
      player.isChecked = false; // Resetar check também
      player.isWinner = false; // Resetar vencedor
      player.cards = ''; // Resetar cartas
    });
    
    // Configurar apostas iniciais dos blinds
    if (this.currentHand.blinds.small > 0 || this.currentHand.blinds.big > 0) {
      console.log(`💰 DEBUG: Configurando apostas iniciais dos blinds`);
      
      // Encontrar Small Blind
      const smallBlindPlayer = this.currentHand.players.find(p => p.isSmallBlind);
      if (smallBlindPlayer) {
        smallBlindPlayer.bet = this.currentHand.blinds.small;
        smallBlindPlayer.currentBet = this.currentHand.blinds.small;
        console.log(`💰 DEBUG: ${smallBlindPlayer.name} (SB) apostou $${this.currentHand.blinds.small}`);
      }
      
      // Encontrar Big Blind
      const bigBlindPlayer = this.currentHand.players.find(p => p.isBigBlind);
      if (bigBlindPlayer) {
        bigBlindPlayer.bet = this.currentHand.blinds.big;
        bigBlindPlayer.currentBet = this.currentHand.blinds.big;
        console.log(`💰 DEBUG: ${bigBlindPlayer.name} (BB) apostou $${this.currentHand.blinds.big}`);
      }
    }
  }

  /**
   * Complete replay - Garante que todas as ações sejam processadas até o final
   */
  private completeReplay(): void {
    if (!this.currentHand) return;

    console.log('🏆 DEBUG: Completando replay - identificando vencedor');
    console.log(`🔍 DEBUG: currentActionIndex atual: ${this.currentActionIndex}`);
    console.log(`🔍 DEBUG: total de ações: ${this.currentHand.actions.length}`);
    
    // Processar apenas as ações restantes (não todas novamente)
    const startIndex = this.currentActionIndex + 1;
    console.log(`🔍 DEBUG: Processando ações de ${startIndex} até ${this.currentHand.actions.length - 1}`);
    
    for (let i = startIndex; i < this.currentHand.actions.length; i++) {
      this.currentActionIndex = i;
      const action = this.currentHand.actions[i];
      console.log(`🔍 DEBUG: Processando ação final ${i}: ${action.player} - ${action.action} - ${action.street}`);
      this.processAction(action);
    }

    // Aguardar um pouco para garantir que todas as ações foram processadas
    setTimeout(() => {
      this.showFinalResult();
    }, 1000);
  }

  /**
   * Show final result after replay completes
   */
  private showFinalResult(): void {
    if (!this.currentHand) return;

    // Identificar o vencedor usando as ações do SUMMARY
    let winner = null;
    let finalPot = this.pot;

    // Procurar por ações de "collected" ou "won" no SUMMARY
    const collectedAction = this.currentHand.actions.find(a => 
      a.action === 'collected' && a.street === 'summary'
    );
    
    if (collectedAction) {
      winner = this.currentHand.players.find(p => p.name === collectedAction.player);
      finalPot = collectedAction.amount || this.pot;
      console.log(`🏆 DEBUG: Vencedor por collected: ${collectedAction.player} - $${finalPot}`);
    } else {
      // Fallback: último jogador ativo
      const activePlayers = this.currentHand.players.filter(p => !p.isFolded);
      if (activePlayers.length === 1) {
        winner = activePlayers[0];
        console.log(`🏆 DEBUG: Vencedor único: ${winner.name}`);
      } else {
        console.log('⚠️  DEBUG: Não foi possível identificar o vencedor');
        console.log('🔍 DEBUG: Jogadores ativos:', activePlayers.map(p => p.name));
        console.log('🔍 DEBUG: Todas as ações:', this.currentHand.actions);
      }
    }

    // Exibir resultado final
    if (winner) {
      console.log(`🎉 RESULTADO FINAL: ${winner.name} ganhou $${finalPot}`);
      
      // Mostrar cartas do vencedor se disponível
      if (winner.cards) {
        console.log(`🃏 Cartas do vencedor: ${winner.cards}`);
      }
      
      // Aqui você pode adicionar uma notificação visual ou modal
      alert(`🎉 ${winner.name} ganhou $${finalPot}!${winner.cards ? `\nCartas: ${winner.cards}` : ''}`);
    }

    this.isPlaying = false;
    this.handComplete.emit(this.currentHand);
  }

  /**
   * Skip to specific action
   */
  skipToAction(index: number): void {
    if (!this.currentHand || index < -1 || index >= this.currentHand.actions.length) return;

    this.stopReplay();
    this.currentActionIndex = index;
    this.visibleActions = [];
    this.resetBoard();
    this.resetPot();
    this.resetPlayerStates();

    // Process all actions up to the target index
    for (let i = 0; i <= index; i++) {
      const action = this.currentHand.actions[i];
      this.processAction(action);
      this.visibleActions.push(action);
    }
  }

  /**
   * Get progress percentage
   */
  getProgress(): number {
    if (!this.currentHand || this.currentHand.actions.length === 0) return 0;
    return ((this.currentActionIndex + 1) / this.currentHand.actions.length) * 100;
  }

  /**
   * Format card for display
   */
  formatCard(card: string): string {
    if (!card) return '';
    
    const rank = card.charAt(0);
    const suit = card.charAt(1);
    
    const suitSymbols: { [key: string]: string } = {
      'h': '♥',
      'd': '♦',
      'c': '♣',
      's': '♠'
    };

    return `${rank}${suitSymbols[suit] || suit}`;
  }

  /**
   * Get card color class
   */
  getCardColor(card: string): string {
    if (!card) return 'black';
    
    const suit = card.slice(-1).toLowerCase();
    return (suit === 'h' || suit === 'd') ? 'red' : 'black';
  }

  getCardSuit(card: string): string {
    if (!card) return '';
    
    const suit = card.slice(-1).toLowerCase();
    switch (suit) {
      case 'h': return '♥';
      case 'd': return '♦';
      case 'c': return '♣';
      case 's': return '♠';
      default: return suit;
    }
  }

  /**
   * Format amount for display
   */
  formatAmount(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  }

  /**
   * Get player position on table
   */
  getPlayerPosition(index: number): { x: number; y: number } {
    if (!this.currentHand) return { x: 0, y: 0 };

    const totalPlayers = this.currentHand.players.length;
    const angle = (index * 360 / totalPlayers) - 90; // Start from top
    const radius = 42; // Aumentado para posicionar no limite da mesa (era 35)

    const x = 50 + radius * Math.cos(angle * Math.PI / 180);
    const y = 50 + radius * Math.sin(angle * Math.PI / 180);

    return { x, y };
  }

  /**
   * Gera fichas visuais baseadas no valor da aposta
   */
  generateChips(betAmount: number): Array<{color: string, value: number, count: number}> {
    console.log(`🔍 DEBUG: generateChips - betAmount: ${betAmount}`);
    
    const chips: Array<{color: string, value: number, count: number}> = [];
    
    // Valores padrão de fichas
    const chipValues = [
      { value: 1000, color: '#8B0000' }, // Vermelho escuro
      { value: 500, color: '#FF0000' },  // Vermelho
      { value: 100, color: '#0000FF' },  // Azul
      { value: 25, color: '#008000' },   // Verde
      { value: 5, color: '#FFD700' },    // Dourado
      { value: 1, color: '#FFFFFF' }     // Branco
    ];
    
    let remainingAmount = betAmount;
    
    for (const chip of chipValues) {
      if (remainingAmount >= chip.value) {
        const count = Math.floor(remainingAmount / chip.value);
        chips.push({
          color: chip.color,
          value: chip.value,
          count: count
        });
        remainingAmount -= count * chip.value;
      }
    }
    
    console.log(`🔍 DEBUG: generateChips - result:`, chips);
    return chips;
  }

  /**
   * Obtém cor da ficha baseada no valor
   */
  getChipColor(value: number): string {
    const chipColors: {[key: number]: string} = {
      1: '#FFFFFF',    // Branco
      5: '#FFD700',    // Dourado
      25: '#008000',   // Verde
      100: '#0000FF',  // Azul
      500: '#FF0000',  // Vermelho
      1000: '#8B0000'  // Vermelho escuro
    };
    
    return chipColors[value] || '#CCCCCC';
  }

  /**
   * Toggle play/pause
   */
  togglePlay(): void {
    if (!this.isPlaying) {
      this.startReplay();
    } else if (this.isPaused) {
      this.resumeReplay();
    } else {
      this.pauseReplay();
    }
  }

  /**
   * Previous hand
   */
  previousHand(): void {
    // TODO: Implement when multiple hands are supported
    console.log('Previous hand');
  }

  /**
   * Next hand
   */
  nextHand(): void {
    // TODO: Implement when multiple hands are supported
    console.log('Next hand');
  }

  /**
   * Can go to previous hand
   */
  canGoPreviousHand(): boolean {
    // TODO: Implement when multiple hands are supported
    return false;
  }

  /**
   * Can go to next hand
   */
  canGoNextHand(): boolean {
    // TODO: Implement when multiple hands are supported
    return false;
  }

  /**
   * Share hand
   */
  shareHand(): void {
    if (this.currentHand) {
      const handText = this.handHistory;
      navigator.clipboard.writeText(handText).then(() => {
        console.log('Hand history copied to clipboard');
        // You could show a toast notification here
      });
    }
  }

  /**
   * Toggle fullscreen
   */
  toggleFullscreen(): void {
    if (!document.fullscreenElement) {
      const element = document.querySelector('.riropo-replayer');
      if (element) {
        element.requestFullscreen();
      }
    } else {
      document.exitFullscreen();
    }
  }

  /**
   * Previous action
   */
  previousAction(): void {
    if (this.currentActionIndex > 0 && this.currentHand) {
      this.currentActionIndex--;
      console.log(`🔍 DEBUG: previousAction - indo para ação ${this.currentActionIndex}`);
      
      // Processar apenas a ação atual sem reprocessar todas as anteriores
      const action = this.currentHand.actions[this.currentActionIndex];
      console.log(`🔍 DEBUG: previousAction - processando ação ${this.currentActionIndex}: ${action.player} - ${action.action}`);
      
      // Atualizar street se necessário
      if (action.street !== this.currentStreet) {
        console.log(`🔍 DEBUG: previousAction - mudando street: ${this.currentStreet} -> ${action.street}`);
        this.currentStreet = action.street;
        this.updateBoard();
        this.clearPlayerBets();
      }
      
      this.processAction(action);
      this.visibleActions.push(action);
    }
  }

  /**
   * Next action
   */
  nextAction(): void {
    if (this.currentHand && this.currentActionIndex < this.currentHand.actions.length - 1) {
      this.currentActionIndex++;
      console.log(`🔍 DEBUG: nextAction - indo para ação ${this.currentActionIndex}`);
      
      // Processar apenas a ação atual sem reprocessar todas as anteriores
      const action = this.currentHand.actions[this.currentActionIndex];
      console.log(`🔍 DEBUG: nextAction - processando ação ${this.currentActionIndex}: ${action.player} - ${action.action}`);
      
      // Se a street mudou, primeiro mostrar apenas as cartas
      if (action.street !== this.currentStreet) {
        console.log(`🔍 DEBUG: nextAction - mudando street: ${this.currentStreet} -> ${action.street}`);
        this.currentStreet = action.street;
        this.updateBoard();
        this.clearPlayerBets();
        console.log(`🔍 DEBUG: nextAction - cartas da nova street mostradas`);
        return; // Parar aqui, próxima ação processará a primeira ação da nova street
      }
      
      // Processar a ação normalmente
      this.processAction(action);
      this.visibleActions.push(action);
    }
  }

  /**
   * Can go to previous action
   */
  canGoPrevious(): boolean {
    return this.currentActionIndex > 0;
  }

  /**
   * Can go to next action
   */
  canGoNext(): boolean {
    return !!(this.currentHand && this.currentActionIndex < this.currentHand.actions.length - 1);
  }

  /**
   * Reset to start of hand
   */
  resetToStart(): void {
    this.currentActionIndex = -1;
    this.updateReplayState();
  }

  /**
   * Go to end of hand
   */
  goToEnd(): void {
    if (this.currentHand) {
      this.currentActionIndex = this.currentHand.actions.length - 1;
      this.updateReplayState();
    }
  }

  /**
   * Previous street
   */
  previousStreet(): void {
    // TODO: Implement street navigation
    console.log('Previous street');
  }

  /**
   * Next street
   */
  nextStreet(): void {
    // TODO: Implement street navigation
    console.log('Next street');
  }

  /**
   * Can go to previous street
   */
  canGoPreviousStreet(): boolean {
    // TODO: Implement street navigation
    return false;
  }

  /**
   * Can go to next street
   */
  canGoNextStreet(): boolean {
    // TODO: Implement street navigation
    return false;
  }

  /**
   * Toggle play/pause
   */
  togglePlayPause(): void {
    if (this.isPlaying) {
      if (this.isPaused) {
        this.resumeReplay();
      } else {
        this.pauseReplay();
      }
    } else {
      this.startReplay();
    }
  }

  /**
   * Get progress percentage
   */
  getProgressPercentage(): number {
    if (!this.currentHand || this.currentHand.actions.length === 0) return 0;
    return ((this.currentActionIndex + 1) / this.currentHand.actions.length) * 100;
  }

  /**
   * Get total actions count
   */
  get totalActions(): number {
    return this.currentHand?.actions.length || 0;
  }

  /**
   * Update replay state based on current action index
   */
  private updateReplayState(): void {
    if (!this.currentHand) return;

    console.log(`🔍 DEBUG: updateReplayState - INÍCIO`);
    console.log(`🔍 DEBUG: updateReplayState - currentActionIndex: ${this.currentActionIndex}`);
    console.log(`🔍 DEBUG: updateReplayState - visibleActions.length: ${this.visibleActions.length}`);
    
    // Log de todas as ações disponíveis
    console.log(`🔍 DEBUG: Todas as ações disponíveis:`);
    this.visibleActions.forEach((action, index) => {
      console.log(`  ${index}: ${action.player} - ${action.action} - ${action.street}`);
    });

    // Processar ações até o índice atual
    this.visibleActions.slice(0, this.currentActionIndex + 1).forEach(action => {
      this.processAction(action);
    });

    console.log(`🔍 DEBUG: updateReplayState - finalizado, ${this.visibleActions.length} ações processadas`);
  }
} 