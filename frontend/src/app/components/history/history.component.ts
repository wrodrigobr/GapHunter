import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';

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

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, FormsModule],
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
    order_by: 'date_desc'
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
    return cards.replace(/([AKQJT98765432])([shdc])/g, '$1<span class="suit-$2">$2</span>');
  }

  openAnalysisModal(hand: Hand) {
    this.selectedHand = hand;
    this.showAnalysisModal = true;
  }

  closeAnalysisModal() {
    this.selectedHand = null;
    this.showAnalysisModal = false;
  }

  clearFilters() {
    this.filters = {
      gap_filter: 'all',
      position_filter: '',
      action_filter: '',
      date_from: '',
      date_to: '',
      order_by: 'date_desc'
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
}

