import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { PokerReplayerComponent } from '../poker-replayer/poker-replayer.component';
import { RiropoParserService, RiropoHand } from '../../services/riropo-parser.service';
import { HandReplay, PlayerInfo, PlayerAction, GameStreet } from '../../models/hand-replay.model';

@Component({
  selector: 'app-poker-table',
  standalone: true,
  imports: [CommonModule, FormsModule, PokerReplayerComponent],
  templateUrl: './poker-table.component.html',
  styleUrls: ['./poker-table.component.scss']
})
export class PokerTableComponent implements OnInit, OnChanges, OnDestroy {
  @Input() handReplay: HandReplay | null = null;
  @Input() currentStreetIndex: number = 0;
  @Input() currentActionIndex: number = 0;

  // Configuração da mesa
  tableConfig: PokerTableConfig = POKERSTARS_CONFIG;
  
  // Elementos open source para uso no template
  readonly openSourceElements = OPEN_SOURCE_ELEMENTS;
  
  // RIROPO Replayer properties
  handHistoryText: string = '';
  showReplayer: boolean = false;
  
  // Estado atual da mesa
  currentPlayers: PlayerInfo[] = [];
  currentBoardCards: string[] = [];
  currentPot: number = 0;
  currentStreet: string = 'preflop';
  isFullscreen: boolean = false;
  
  // Fichas dinâmicas
  dynamicChips: Array<{x: number, y: number, flying: boolean}> = [];
  winner: string | null = null;
  showWinnerAnimation: boolean = false;
  
  // Array para uso no template
  Array = Array;
  
  // Posições na mesa (coordenadas para 9 jogadores)
  seatPositions = [
    { x: 50, y: 90 },   // Seat 1 - Bottom center (mais baixo)
    { x: 20, y: 75 },   // Seat 2 - Bottom left (melhor posicionado)
    { x: 8, y: 45 },    // Seat 3 - Middle left (mais próximo da borda)
    { x: 20, y: 12 },   // Seat 4 - Top left (melhor posicionado)
    { x: 50, y: 2 },    // Seat 5 - Top center (mais alto)
    { x: 80, y: 12 },   // Seat 6 - Top right (melhor posicionado)
    { x: 92, y: 45 },   // Seat 7 - Middle right (mais próximo da borda)
    { x: 80, y: 75 },   // Seat 8 - Bottom right (melhor posicionado)
    { x: 70, y: 90 }    // Seat 9 - Bottom right center (mais baixo)
  ];

  ngOnInit() {
    this.initializeTable();
    this.setupKeyboardShortcuts();
    this.applyPokerStarsTheme();
  }

  /**
   * Load hand history into RIROPO replayer
   */
  loadHandHistory(): void {
    if (this.handHistoryText.trim()) {
      this.showReplayer = true;
    }
  }

  /**
   * Load hand from database and convert to RIROPO format
   */
  loadHandFromDatabase(): void {
    if (this.handReplay) {
      console.log('📊 Convertendo dados para formato RIROPO...');
      const riropoHandText = this.convertHandReplayToRiropoFormat(this.handReplay);
      this.handHistoryText = riropoHandText;
      this.showReplayer = true;
      console.log('✅ Mesa RIROPO carregada com sucesso!');
      console.log('📝 Hand history convertido:', riropoHandText.substring(0, 200) + '...');
    } else {
      console.log('❌ Nenhum handReplay disponível para carregar');
    }
  }

  /**
   * Convert HandReplay from database to RIROPO format
   */
  private convertHandReplayToRiropoFormat(handReplay: HandReplay): string {
    console.log('🔍 DEBUG: Convertendo HandReplay para formato RIROPO...');
    console.log('📊 DEBUG: HandReplay original:', handReplay);
    
    let riropoText = '';
    
    // Header - formato exato do PokerStars
    riropoText += `PokerStars Hand #${handReplay.hand_id}: Hold'em No Limit ($${handReplay.blinds.small}/${handReplay.blinds.big})\n`;
    riropoText += `Table '${handReplay.table_name}' ${handReplay.level}\n`;
    
    // Encontrar button
    const buttonPlayer = handReplay.players.find(p => p.is_button);
    console.log('🔍 DEBUG: Button player encontrado:', buttonPlayer);
    riropoText += `Seat #${buttonPlayer?.position || 1} is the button\n`;
    
    // Players - formato exato
    handReplay.players.forEach((player, index) => {
      console.log(`🔍 DEBUG: Player ${index + 1} - ${player.name}:`);
      console.log(`  - Position: ${player.position}`);
      console.log(`  - is_button: ${player.is_button}`);
      console.log(`  - is_small_blind: ${player.is_small_blind}`);
      console.log(`  - is_big_blind: ${player.is_big_blind}`);
      console.log(`  - is_hero: ${player.is_hero}`);
      
      // Adicionar informações de blind diretamente no texto do jogador
      let playerText = `Seat ${player.position}: ${player.name} ($${player.stack} in chips)`;
      
      if (player.is_button) {
        playerText += ' [BTN]';
      }
      if (player.is_small_blind) {
        playerText += ' [SB]';
      }
      if (player.is_big_blind) {
        playerText += ' [BB]';
      }
      
      riropoText += playerText + '\n';
    });
    
    // Blinds - formato exato
    const sbPlayer = handReplay.players.find(p => p.is_small_blind);
    const bbPlayer = handReplay.players.find(p => p.is_big_blind);
    console.log('🔍 DEBUG: Small blind player:', sbPlayer);
    console.log('🔍 DEBUG: Big blind player:', bbPlayer);
    
    if (sbPlayer) {
      riropoText += `${sbPlayer.name}: posts small blind $${handReplay.blinds.small}\n`;
    }
    if (bbPlayer) {
      riropoText += `${bbPlayer.name}: posts big blind $${handReplay.blinds.big}\n`;
    }
    
    // Hole cards
    riropoText += '\n*** HOLE CARDS ***\n';
    const heroPlayer = handReplay.players.find(p => p.is_hero);
    if (heroPlayer && handReplay.hero_cards && handReplay.hero_cards.length > 0) {
      riropoText += `Dealt to ${heroPlayer.name} [${handReplay.hero_cards.join(' ')}]\n`;
    }
    
    // Streets and actions
    handReplay.streets.forEach(street => {
      console.log(`🔍 DEBUG: Processando street: ${street.name}`);
      console.log(`🔍 DEBUG: Cartas da street:`, street.cards);
      
      riropoText += `\n*** ${street.name.toUpperCase()} ***\n`;
      
      // Board cards - formato correto
      if (street.cards && street.cards.length > 0) {
        console.log(`🔍 DEBUG: Board cards for ${street.name}:`, street.cards);
        riropoText += `[${street.cards.join(' ')}]\n`;
      } else {
        console.log(`⚠️  DEBUG: No board cards for ${street.name}`);
      }
      
      // Actions - formato exato
      street.actions.forEach(action => {
        let actionText = `${action.player}: `;
        switch (action.action.toLowerCase()) {
          case 'fold':
            actionText += 'folds';
            break;
          case 'check':
            actionText += 'checks';
            break;
          case 'call':
            actionText += `calls $${action.amount}`;
            break;
          case 'bet':
            actionText += `bets $${action.amount}`;
            break;
          case 'raise':
            actionText += `raises $${action.amount} to $${action.total_bet}`;
            break;
          case 'all-in':
            actionText += `all-in $${action.amount}`;
            break;
          default:
            actionText += action.action;
        }
        riropoText += actionText + '\n';
      });
    });
    
    // Summary - formato exato
    riropoText += '\n*** SUMMARY ***\n';
    const totalPot = this.calculateTotalPot(handReplay);
    riropoText += `Total pot $${totalPot} | Rake $0\n`;
    
    // Board final
    const allBoardCards = handReplay.streets.flatMap(s => s.cards);
    if (allBoardCards.length > 0) {
      riropoText += `Board [${allBoardCards.join(' ')}]\n`;
    }
    
    // Player summaries
    handReplay.players.forEach(player => {
      let summary = `Seat ${player.position}: ${player.name}`;
      
      if (player.is_button) {
        summary += ' (button)';
      } else if (player.is_small_blind) {
        summary += ' (small blind)';
      } else if (player.is_big_blind) {
        summary += ' (big blind)';
      }
      
      // Determinar resultado
      const lastAction = this.getLastActionForPlayer(player.name, handReplay.streets);
      if (lastAction && lastAction.street) {
        if (lastAction.action.toLowerCase() === 'fold') {
          summary += ` folded on the ${this.getStreetName(lastAction.street)}`;
        } else if (lastAction.action.toLowerCase() === 'call' || lastAction.action.toLowerCase() === 'check') {
          summary += ` showed and won ($${totalPot})`;
        }
      } else {
        summary += ' folded before Flop';
      }
      
      riropoText += summary + '\n';
    });
    
    return riropoText;
  }

  /**
   * Get last action for a specific player
   */
  private getLastActionForPlayer(playerName: string, streets: GameStreet[]): PlayerAction | null {
    for (let i = streets.length - 1; i >= 0; i--) {
      const street = streets[i];
      for (let j = street.actions.length - 1; j >= 0; j--) {
        const action = street.actions[j];
        if (action.player === playerName) {
          // Adicionar a propriedade street se não existir
          if (!action.street) {
            action.street = street.name;
          }
          return action;
        }
      }
    }
    return null;
  }

  /**
   * Get street name for summary
   */
  private getStreetName(street: string): string {
    switch (street.toLowerCase()) {
      case 'preflop': return 'Preflop';
      case 'flop': return 'Flop';
      case 'turn': return 'Turn';
      case 'river': return 'River';
      default: return street;
    }
  }

  /**
   * Calculate total pot from all streets
   */
  private calculateTotalPot(handReplay: HandReplay): number {
    let total = handReplay.blinds.small + handReplay.blinds.big;
    if (handReplay.blinds.ante) {
      total += handReplay.blinds.ante;
    }
    
    handReplay.streets.forEach(street => {
      street.actions.forEach(action => {
        if (action.amount > 0) {
          total += action.amount;
        }
      });
    });
    
    return total;
  }

  /**
   * Handle hand completion from RIROPO replayer
   */
  onHandComplete(hand: RiropoHand): void {
    console.log('Hand completed:', hand);
    // You can add additional logic here when hand replay is complete
  }

  ngOnDestroy() {
    this.removeKeyboardShortcuts();
  }

  /**
   * Aplica tema do PokerStars
   */
  private applyPokerStarsTheme(): void {
    PokerTableUtils.applyTheme(this.tableConfig);
  }

  private setupKeyboardShortcuts() {
    document.addEventListener('keydown', this.handleKeyDown.bind(this));
  }

  private removeKeyboardShortcuts() {
    document.removeEventListener('keydown', this.handleKeyDown.bind(this));
  }

  private handleKeyDown(event: KeyboardEvent) {
    // Só processar se não estiver em um input ou textarea
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
      return;
    }

    switch (event.key) {
      case 'ArrowLeft':
        event.preventDefault();
        this.previousAction();
        break;
      case 'ArrowRight':
      case ' ':
        event.preventDefault();
        this.nextAction();
        break;
      case 'Home':
        event.preventDefault();
        this.resetToStart();
        break;
      case 'End':
        event.preventDefault();
        this.goToEnd();
        break;
      case 'PageUp':
        event.preventDefault();
        this.previousStreet();
        break;
      case 'PageDown':
        event.preventDefault();
        this.nextStreet();
        break;
    }
  }

  goToEnd() {
    if (!this.handReplay) return;
    
    this.currentStreetIndex = this.handReplay.streets.length - 1;
    const lastStreet = this.handReplay.streets[this.currentStreetIndex];
    this.currentActionIndex = lastStreet ? lastStreet.actions.length - 1 : 0;
    this.updateTableState();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['handReplay'] || changes['currentStreetIndex'] || changes['currentActionIndex']) {
      this.updateTableState();
      
      // Se há dados do handReplay, automaticamente carregar a mesa RIROPO
      if (changes['handReplay'] && this.handReplay) {
        console.log('🔄 Carregando mesa RIROPO automaticamente...');
        this.loadHandFromDatabase();
      }
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

    // Resetar estado do ganhador
    this.winner = null;
    this.showWinnerAnimation = false;
    this.dynamicChips = [];

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

    // Aplicar blinds
    this.currentPlayers.forEach(player => {
      if (player.is_small_blind) {
        const blindAmount = this.handReplay!.blinds.small;
        player.current_bet = blindAmount;
        player.stack = Math.max(0, player.stack - blindAmount);
      } else if (player.is_big_blind) {
        const blindAmount = this.handReplay!.blinds.big;
        player.current_bet = blindAmount;
        player.stack = Math.max(0, player.stack - blindAmount);
      }
    });

    // Aplicar antes para todos os jogadores (antes são pagas por todos)
    if (this.handReplay.blinds.ante > 0) {
      this.currentPlayers.forEach(player => {
        if (!player.current_bet) {
          player.current_bet = 0;
        }
        player.current_bet += this.handReplay!.blinds.ante;
        player.stack = Math.max(0, player.stack - this.handReplay!.blinds.ante);
      });
    }
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

    // Adicionar fichas dinâmicas para apostas
    if (action.action === 'call' || action.action === 'raise' || action.action === 'bet' || action.action === 'all-in') {
      this.addDynamicChip(action);
    }

    switch (action.action) {
      case 'fold':
        player.is_folded = true;
        player.is_active = false;
        break;
      case 'call':
        // Calcular quanto o jogador precisa pagar
        const callAmount = action.amount - (player.current_bet || 0);
        if (callAmount > 0) {
          player.stack = Math.max(0, player.stack - callAmount);
        player.current_bet = action.amount;
        }
        break;
      case 'raise':
      case 'bet':
        // Calcular quanto o jogador precisa pagar
        const betAmount = action.amount - (player.current_bet || 0);
        if (betAmount > 0) {
          player.stack = Math.max(0, player.stack - betAmount);
        player.current_bet = action.amount;
        }
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

  addDynamicChip(action: PlayerAction) {
    const player = this.currentPlayers.find(p => p.name === action.player);
    if (!player) return;

    const playerPos = this.getPlayerPosition(player.position);
    
    // Calcular posição inicial da ficha (jogador) - ajustado para posicionamento mais preciso
    const startX = (playerPos.x / 100) * 1200; // Converter % para px (assumindo largura de 1200px)
    const startY = (playerPos.y / 100) * 600;  // Converter % para px (assumindo altura de 600px)
    
    // Posição final (centro do pote - 20% do topo, 50% da esquerda)
    const endX = 600; // Centro horizontal
    const endY = 120; // Centro do pote (20% do topo)
    
    // Adicionar ficha com animação
    this.dynamicChips.push({
      x: startX,
      y: startY,
      flying: true
    });

    // Animar movimento da ficha
    setTimeout(() => {
      const chip = this.dynamicChips.find(c => c.x === startX && c.y === startY);
      if (chip) {
        chip.x = endX;
        chip.y = endY;
      }
    }, 100);

    // Remover ficha após animação
    setTimeout(() => {
      this.dynamicChips = this.dynamicChips.filter(chip => chip.x !== startX || chip.y !== startY);
    }, 1500);
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
    const breakdown = this.getPotBreakdown();
    this.currentPot = breakdown.blinds + breakdown.antes + breakdown.bets;
    
    // Verificar se chegamos ao final da mão para determinar o ganhador
    if (this.isHandComplete()) {
      this.determineWinner();
    }
  }

  isHandComplete(): boolean {
    if (!this.handReplay) return false;
    
    // Verificar se estamos na última street e na última ação
    const isLastStreet = this.currentStreetIndex === this.handReplay.streets.length - 1;
    if (!isLastStreet) return false;
    
    const lastStreet = this.handReplay.streets[this.currentStreetIndex];
    const isLastAction = this.currentActionIndex === lastStreet.actions.length - 1;
    
    return isLastAction;
  }

  determineWinner() {
    if (!this.handReplay) return;
    
    // Lógica simplificada: o último jogador ativo é o ganhador
    const activePlayers = this.currentPlayers.filter(p => !p.is_folded);
    
    if (activePlayers.length === 1) {
      this.winner = activePlayers[0].name;
      this.showWinnerAnimation = true;
      this.distributePotToWinner();
    } else if (activePlayers.length > 1) {
      // Em caso de empate, o primeiro jogador ativo é considerado ganhador
      this.winner = activePlayers[0].name;
      this.showWinnerAnimation = true;
      this.distributePotToWinner();
    }
  }

  distributePotToWinner() {
    if (!this.winner) return;
    
    const winnerPlayer = this.currentPlayers.find(p => p.name === this.winner);
    if (winnerPlayer) {
      // Adicionar o pote ao stack do ganhador
      winnerPlayer.stack += this.currentPot;
      
      // Animar fichas voando para o ganhador
      this.animatePotToWinner();
    }
  }

  animatePotToWinner() {
    if (!this.winner) return;
    
    const winnerPlayer = this.currentPlayers.find(p => p.name === this.winner);
    if (!winnerPlayer) return;
    
    const winnerPos = this.getPlayerPosition(winnerPlayer.position);
    
    // Criar múltiplas fichas voando do pote para o ganhador
    for (let i = 0; i < 5; i++) {
      setTimeout(() => {
        this.dynamicChips.push({
          x: 600, // Centro do pote
          y: 120, // Centro do pote
          flying: true
        });
        
        // Animar movimento para o ganhador
        setTimeout(() => {
          const chip = this.dynamicChips[this.dynamicChips.length - 1];
          if (chip) {
            chip.x = (winnerPos.x / 100) * 1200;
            chip.y = (winnerPos.y / 100) * 600;
          }
        }, 100);
        
        // Remover ficha após animação
        setTimeout(() => {
          this.dynamicChips.pop();
        }, 2000);
      }, i * 200);
    }
  }

  getPotBreakdown(): { blinds: number, antes: number, bets: number } {
    if (!this.handReplay) return { blinds: 0, antes: 0, bets: 0 };

    // Blinds sempre contabilizados
    const blinds = this.handReplay.blinds.small + this.handReplay.blinds.big;
    
    // Antes contabilizadas para todos os jogadores ativos (não foldados)
    const antes = this.handReplay.blinds.ante > 0 ? 
      this.handReplay.blinds.ante * this.currentPlayers.filter(p => !p.is_folded).length : 0;
    
    // Apostas atuais dos jogadores
    const bets = this.currentPlayers.reduce((total, player) => {
      return total + (player.current_bet || 0);
    }, 0);

    return { blinds, antes, bets };
  }

  /**
   * Obtém posição do jogador usando configuração
   */
  getPlayerPosition(seat: number): { x: number, y: number } {
    const position = PokerTableUtils.getPlayerPosition(seat, this.tableConfig);
    return { x: position.x, y: position.y };
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

  /**
   * Formata cartas usando configuração do PokerStars
   */
  formatCards(cards: string): string {
    if (!cards) return '';
    
    return cards.replace(/([AKQJT98765432])([shdc])/g, (match, rank, suit) => {
      return PokerTableUtils.formatCard(match, this.tableConfig.cardStyle);
    });
  }

  getCardRank(card: string): string {
    if (!card) return '';
    return card.charAt(0);
  }

  getCardSuit(card: string): string {
    if (!card || card.length < 2) return '';
    return card.charAt(1);
  }

  getCardSuitSymbol(card: string): string {
    const suit = this.getCardSuit(card);
    const suitIcons: { [key: string]: string } = {
      's': '♠',
      'h': '♥',
      'd': '♦',
      'c': '♣'
    };
    return suitIcons[suit] || '';
  }

  getCardSuitColor(card: string): string {
    const suit = this.getCardSuit(card);
    return (suit === 'h' || suit === 'd') ? '#d32f2f' : '#000000';
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

  getStackChange(player: PlayerInfo): number {
    if (!this.handReplay) return 0;
    
    // Encontrar o stack inicial do jogador
    const initialPlayer = this.handReplay.players.find(p => p.name === player.name);
    if (!initialPlayer) return 0;
    
    return player.stack - initialPlayer.stack;
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
    this.winner = null;
    this.showWinnerAnimation = false;
    this.dynamicChips = [];
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

  shouldShowChips(player: PlayerInfo): boolean {
    return Boolean(player.current_bet && player.current_bet > 0);
  }

  getPlayerChips(player: PlayerInfo): Array<{count: number, class: string}> {
    if (!player.current_bet || player.current_bet <= 0) {
      return [];
    }

    const chipTypes = [
      { value: 100, class: 'chip-red' },
      { value: 25, class: 'chip-green' },
      { value: 5, class: 'chip-blue' },
      { value: 1, class: 'chip-white' }
    ];

    const chips: Array<{count: number, class: string}> = [];
    let remainingBet = player.current_bet;

    for (const chipType of chipTypes) {
      if (remainingBet >= chipType.value) {
        const count = Math.floor(remainingBet / chipType.value);
        chips.push({ count, class: chipType.class });
        remainingBet = remainingBet % chipType.value;
      }
    }

    return chips;
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

  /**
   * Obtém cor da ficha baseada no valor
   */
  getChipColor(value: number): string {
    return PokerTableUtils.getChipColor(value);
  }

  /**
   * Reproduz efeito sonoro
   */
  playSound(soundType: string): void {
    if (this.tableConfig.animations.cardFlip) {
      PokerTableUtils.playSound(soundType, this.tableConfig);
    }
  }

  /**
   * Muda o tema da mesa
   */
  changeTheme(event: Event): void {
    const theme = (event.target as HTMLSelectElement).value;
    
    switch (theme) {
      case 'pokerstars':
        // Configurar mesa PokerStars
        this.tableConfig = { 
          theme: 'pokerstars', 
          tableColor: '#0d5016',
          feltTexture: 'smooth'
        };
        break;
      case 'classic':
        // Configurar mesa clássica
        this.tableConfig = { 
          theme: 'classic', 
          tableColor: '#0d5016',
          feltTexture: 'smooth'
        };
        break;
      case 'modern':
        // Configurar mesa moderna
        this.tableConfig = { 
          theme: 'modern', 
          tableColor: '#0d5016',
          feltTexture: 'smooth'
        };
        break;
      default:
        // Configurar mesa padrão
        this.tableConfig = { 
          theme: 'dark', 
          tableColor: '#0d5016',
          feltTexture: 'smooth'
        };
        break;
    }
    
    this.applyPokerStarsTheme();
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

  restartHand() {
    this.currentStreetIndex = 0;
    this.currentActionIndex = 0;
    this.updateTableState();
  }
}