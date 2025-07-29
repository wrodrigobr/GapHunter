import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { PokerTableComponent } from '../poker-table/poker-table.component';

interface Hand {
  id: number;
  hand_id: string;
  pokerstars_tournament_id?: string;
  table_name?: string;
  date_played: string;
  hero_name?: string;
  hero_position?: string;
  hero_cards?: string;
  hero_action?: string;
  pot_size?: number;
  bet_amount?: number;
  board_cards?: string;
  ai_analysis?: string;
  created_at: string;
}

interface FilterOptions {
  positions: string[];
  actions: string[];
  gap_options: Array<{value: string, label: string}>;
  order_options: Array<{value: string, label: string}>;
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
  players: Array<{
    name: string;
    position: number;
    stack: number;
    is_hero: boolean;
    is_button: boolean;
    is_small_blind: boolean;  // Adicionado
    is_big_blind: boolean;    // Adicionado
    cards?: string;
  }>;
  hero_name: string;
  hero_cards: string[];
  streets: Array<{
    name: string;
    cards: string[];
    actions: Array<{
      player: string;
      action: string;
      amount: number;
      total_bet: number;
      timestamp: number;
    }>;
  }>;
  action_sequence: any[];
  gaps_identified: string[];
}

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, FormsModule, PokerTableComponent],
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss']
})
export class HistoryComponent implements OnInit {
  hands: Hand[] = [];
  loading = false;
  totalHands = 0;
  currentPage = 1;
  pageSize = 20;
  totalPages = 0;

  // Filtros
  filters = {
    gap_filter: 'all',
    position_filter: '',
    action_filter: '',
    date_from: '',
    date_to: '',
    order_by: 'date_asc'
  };

  filterOptions: FilterOptions = {
    positions: [],
    actions: [],
    gap_options: [],
    order_options: []
  };

  // Modal de análise
  selectedHand: Hand | null = null;
  showAnalysisModal = false;

  // Dados de replay da mão
  handReplayData: HandReplay | null = null;
  loadingReplay = false;
  currentStreetIndex = 0;
  currentActionIndex = 0;
  
  // Análise de ação específica
  currentActionAnalysis: string | null = null;
  analyzingAction = false;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.loadFilterOptions();
    this.loadHands();
  }

  async loadFilterOptions() {
    try {
      this.apiService.getFilterOptions().subscribe({
        next: (options) => {
          this.filterOptions = options;
        },
        error: (error) => {
          console.error('Erro ao carregar opções de filtro:', error);
        }
      });
    } catch (error) {
      console.error('Erro ao carregar opções de filtro:', error);
    }
  }

  async loadHands() {
    this.loading = true;
    try {
      const skip = (this.currentPage - 1) * this.pageSize;
      
      // Carregar mãos
      this.apiService.getMyHands({
        skip,
        limit: this.pageSize,
        ...this.filters
      }).subscribe({
        next: (hands) => {
          this.hands = hands;
        },
        error: (error) => {
          console.error('Erro ao carregar histórico:', error);
          this.notificationService.error('Erro ao carregar histórico de mãos');
        }
      });

      // Carregar contagem total
      this.apiService.getMyHandsCount(this.filters).subscribe({
        next: (countResponse) => {
          this.totalHands = countResponse.total;
          this.totalPages = Math.ceil(this.totalHands / this.pageSize);
        },
        error: (error) => {
          console.error('Erro ao carregar contagem:', error);
        }
      });

    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
      this.notificationService.error('Erro ao carregar histórico de mãos');
    } finally {
      this.loading = false;
    }
  }

  onFilterChange() {
    this.currentPage = 1;
    this.loadHands();
  }

  onPageChange(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadHands();
    }
  }

  getGapStatus(analysis: string): 'ok' | 'gap' | 'error' {
    if (!analysis) return 'ok';
    
    const lowerAnalysis = analysis.toLowerCase();
    
    if (lowerAnalysis.includes('gap')) return 'gap';
    if (lowerAnalysis.includes('erro') || lowerAnalysis.includes('error') || lowerAnalysis.includes('mistake')) return 'error';
    
    return 'ok';
  }

  getGapStatusLabel(status: string): string {
    switch (status) {
      case 'ok': return 'OK';
      case 'gap': return 'Gap';
      case 'error': return 'Erro';
      default: return 'OK';
    }
  }

  getGapStatusClass(status: string): string {
    switch (status) {
      case 'ok': return 'status-ok';
      case 'gap': return 'status-gap';
      case 'error': return 'status-error';
      default: return 'status-ok';
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatCards(cards: string): string {
    if (!cards) return '-';
    
    // Mapear naipes para ícones
    const suitIcons: { [key: string]: string } = {
      's': '♠', // spades (preto)
      'h': '♥', // hearts (vermelho)
      'd': '♦', // diamonds (vermelho)
      'c': '♣'  // clubs (preto)
    };
    
    // Substituir cartas por formato com ícones
    return cards.replace(/([AKQJT98765432])([shdc])/g, (match, rank, suit) => {
      const icon = suitIcons[suit] || suit;
      const colorClass = (suit === 'h' || suit === 'd') ? 'suit-red' : 'suit-black';
      return `${rank}<span class="${colorClass}">${icon}</span>`;
    });
  }

  openAnalysisModal(hand: Hand) {
    this.selectedHand = hand;
    this.showAnalysisModal = true;
    this.loadHandReplayData(hand.id);
  }

  closeAnalysisModal() {
    this.selectedHand = null;
    this.showAnalysisModal = false;
    this.handReplayData = null;
    this.currentActionAnalysis = null;
    this.resetReplayPosition();
  }

  async loadHandReplayData(handId: number) {
    this.loadingReplay = true;
    this.handReplayData = null;
    
    try {
      this.apiService.getHandReplay(handId).subscribe({
        next: (replayData) => {
          this.handReplayData = replayData;
          this.resetReplayPosition();
          console.log('Dados de replay carregados:', replayData);
        },
        error: (error) => {
          console.error('Erro ao carregar dados de replay:', error);
          this.notificationService.error('Erro ao carregar reprodução da mão');
        },
        complete: () => {
          this.loadingReplay = false;
        }
      });
    } catch (error) {
      console.error('Erro ao carregar dados de replay:', error);
      this.notificationService.error('Erro ao carregar reprodução da mão');
      this.loadingReplay = false;
    }
  }

  resetReplay() {
    this.resetReplayPosition();
    this.currentActionAnalysis = null;
  }

  resetReplayPosition() {
    this.currentStreetIndex = 0;
    this.currentActionIndex = 0;
  }

  async analyzeCurrentAction() {
    if (!this.handReplayData || !this.selectedHand) return;
    
    this.analyzingAction = true;
    this.currentActionAnalysis = null;
    
    try {
      // Obter ação atual
      const currentStreet = this.handReplayData.streets[this.currentStreetIndex];
      const currentAction = currentStreet?.actions[this.currentActionIndex];
      
      if (!currentAction) {
        this.notificationService.warning('Nenhuma ação selecionada para análise');
        return;
      }

      // Preparar dados da ação para análise
      const actionData = {
        street: currentStreet.name,
        player: currentAction.player,
        action: currentAction.action,
        amount: currentAction.amount,
        hero_cards: this.handReplayData.hero_cards,
        community_cards: currentStreet.cards,
        position: this.getPlayerPosition(currentAction.player),
        pot_size: this.calculateCurrentPot(),
        is_hero: currentAction.player === this.handReplayData.hero_name
      };

      this.apiService.analyzeSpecificAction(this.selectedHand.id, actionData).subscribe({
        next: (analysis) => {
          this.currentActionAnalysis = analysis.action_analysis;
        },
        error: (error) => {
          console.error('Erro ao analisar ação:', error);
          this.notificationService.error('Erro ao analisar ação específica');
        },
        complete: () => {
          this.analyzingAction = false;
        }
      });

    } catch (error) {
      console.error('Erro ao analisar ação:', error);
      this.notificationService.error('Erro ao analisar ação específica');
      this.analyzingAction = false;
    }
  }

  private getPlayerPosition(playerName: string): string {
    if (!this.handReplayData) return 'unknown';
    
    const player = this.handReplayData.players.find(p => p.name === playerName);
    if (!player) return 'unknown';
    
    // Lógica simplificada para determinar posição
    if (player.is_button) return 'BTN';
    if (player.is_small_blind) return 'SB';
    if (player.is_big_blind) return 'BB';
    
    return `Pos${player.position}`;
  }

  private calculateCurrentPot(): number {
    if (!this.handReplayData) return 0;
    
    // Cálculo simplificado do pot atual
    let pot = this.handReplayData.blinds.small + this.handReplayData.blinds.big;
    
    // Adicionar antes se houver
    if (this.handReplayData.blinds.ante > 0) {
      pot += this.handReplayData.blinds.ante * this.handReplayData.players.length;
    }
    
    // Adicionar apostas até a ação atual
    for (let streetIndex = 0; streetIndex <= this.currentStreetIndex; streetIndex++) {
      const street = this.handReplayData.streets[streetIndex];
      if (!street) continue;
      
      const maxActionIndex = streetIndex === this.currentStreetIndex ? 
        this.currentActionIndex : street.actions.length - 1;
      
      for (let actionIndex = 0; actionIndex <= maxActionIndex; actionIndex++) {
        const action = street.actions[actionIndex];
        if (action && action.amount > 0) {
          pot += action.amount;
        }
      }
    }
    
    return pot;
  }

  clearFilters() {
    this.filters = {
      gap_filter: 'all',
      position_filter: '',
      action_filter: '',
      date_from: '',
      date_to: '',
      order_by: 'date_asc'
    };
    this.onFilterChange();
  }

  getPageNumbers(): number[] {
    const pages: number[] = [];
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, this.currentPage + 2);
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
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
}

