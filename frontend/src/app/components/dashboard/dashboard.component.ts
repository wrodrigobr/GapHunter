import { Component, OnInit, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AuthService, User } from '../../services/auth.service';
import { ApiService, Hand, UserStats } from '../../services/api.service';
import { UploadService } from '../../services/upload.service';
import { NotificationService } from '../../services/notification.service';
import { UploadProgressComponent } from '../upload-progress/upload-progress.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, UploadProgressComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  @ViewChild('progressChart', { static: false }) progressChartRef!: ElementRef;
  
  currentUser: User | null = null;
  userStats: UserStats | null = null;
  hands: Hand[] = [];
  isLoading = true;
  errorMessage = '';
  selectedFile: File | null = null;
  isUploading = false;
  uploadMessage = '';
  isDragOver = false;

  // Novos dados para indicadores
  streetGaps: Array<{street: string, count: number, percentage: number}> = [];
  positionGaps: Array<{position: string, count: number, percentage: number}> = [];
  totalActions = 0;
  averagePot = 0;
  premiumPositionAggression = 0;
  cbetRate = 0;
  threeBetRate = 0;
  handsThisMonth = 0;
  gapsThisMonth = 0;
  monthlyImprovement = 0;

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private uploadService: UploadService,
    private notificationService: NotificationService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (!user) {
        this.router.navigate(['/auth']);
      }
    });

    this.loadDashboardData();
    
    // Escutar quando o upload for concluído
    this.uploadService.uploadCompleted$.subscribe(completed => {
      if (completed) {
        console.log('🎉 Upload concluído, definindo isUploading como false');
        this.isUploading = false;
        this.uploadService.uploadCompletedSubject.next(false); // Reset para próximo upload
      }
    });
  }

  loadDashboardData() {
    this.isLoading = true;
    
    Promise.all([
      firstValueFrom(this.apiService.getUserStats()),
      firstValueFrom(this.apiService.getUserHands(0, 1000)) // Buscar mais mãos para análise
    ]).then(([stats, hands]) => {
      this.userStats = stats || null;
      this.hands = hands || [];
      this.calculateAdvancedStats();
      this.isLoading = false;
    }).catch(error => {
      console.error('Erro ao carregar dados:', error);
      this.errorMessage = 'Erro ao carregar dados do dashboard';
      this.isLoading = false;
    });
  }

  calculateAdvancedStats() {
    this.calculateGapAnalysis();
    this.calculateActionStats();
    this.calculateFinancialStats();
    this.calculateMonthlyProgress();
  }

  calculateGapAnalysis() {
    // Análise de gaps por street
    const gapsByStreet = new Map<string, number>();
    const totalByStreet = new Map<string, number>();
    
    this.hands.forEach(hand => {
      const street = this.getStreetFromHand(hand);
      totalByStreet.set(street, (totalByStreet.get(street) || 0) + 1);
      
      if (hand.has_gap) {
        gapsByStreet.set(street, (gapsByStreet.get(street) || 0) + 1);
      }
    });

    this.streetGaps = Array.from(totalByStreet.keys()).map(street => ({
      street,
      count: gapsByStreet.get(street) || 0,
      percentage: this.getPercentage(gapsByStreet.get(street) || 0, totalByStreet.get(street) || 1)
    }));

    // Análise de gaps por posição
    const gapsByPosition = new Map<string, number>();
    const totalByPosition = new Map<string, number>();
    
    this.hands.forEach(hand => {
      const position = hand.hero_position || 'unknown';
      totalByPosition.set(position, (totalByPosition.get(position) || 0) + 1);
      
      if (hand.has_gap) {
        gapsByPosition.set(position, (gapsByPosition.get(position) || 0) + 1);
      }
    });

    this.positionGaps = Array.from(totalByPosition.keys()).map(position => ({
      position,
      count: gapsByPosition.get(position) || 0,
      percentage: this.getPercentage(gapsByPosition.get(position) || 0, totalByPosition.get(position) || 1)
    }));
  }

  calculateActionStats() {
    // Calcular total de ações
    this.totalActions = this.hands.reduce((total, hand) => {
      return total + (hand.actions?.length || 0);
    }, 0);

    // Taxa de agressão em posições premium
    const premiumPositions = ['BTN', 'CO', 'HJ'];
    const premiumHands = this.hands.filter(hand => 
      premiumPositions.includes(hand.hero_position || '')
    );
    
    const aggressiveActions = premiumHands.filter(hand => 
      ['raise', 'bet', 'all-in'].includes(hand.hero_action || '')
    ).length;

    this.premiumPositionAggression = this.getPercentage(aggressiveActions, premiumHands.length);

    // Taxa de C-Bet (simplificado)
    const flopHands = this.hands.filter(hand => 
      hand.board_cards && hand.board_cards.length >= 6
    );
    const cbetHands = flopHands.filter(hand => 
      hand.hero_action === 'bet' || hand.hero_action === 'raise'
    ).length;
    
    this.cbetRate = this.getPercentage(cbetHands, flopHands.length);

    // Taxa de 3-Bet (simplificado)
    const threeBetHands = this.hands.filter(hand => 
      hand.hero_action === 'raise' && hand.bet_amount && hand.bet_amount > 0
    ).length;
    
    this.threeBetRate = this.getPercentage(threeBetHands, this.hands.length);
  }

  calculateFinancialStats() {
    // Pot médio
    const totalPot = this.hands.reduce((sum, hand) => sum + (hand.pot_size || 0), 0);
    this.averagePot = this.hands.length > 0 ? totalPot / this.hands.length : 0;
  }

  calculateMonthlyProgress() {
    const now = new Date();
    const thisMonth = now.getMonth();
    const thisYear = now.getFullYear();

    // Mãos deste mês
    this.handsThisMonth = this.hands.filter(hand => {
      const handDate = new Date(hand.date_played);
      return handDate.getMonth() === thisMonth && handDate.getFullYear() === thisYear;
    }).length;

    // Gaps deste mês
    this.gapsThisMonth = this.hands.filter(hand => {
      const handDate = new Date(hand.date_played);
      return handDate.getMonth() === thisMonth && 
             handDate.getFullYear() === thisYear && 
             hand.has_gap;
    }).length;

    // Melhoria mensal (simplificado)
    const lastMonth = thisMonth === 0 ? 11 : thisMonth - 1;
    const lastYear = thisMonth === 0 ? thisYear - 1 : thisYear;
    
    const lastMonthHands = this.hands.filter(hand => {
      const handDate = new Date(hand.date_played);
      return handDate.getMonth() === lastMonth && handDate.getFullYear() === lastYear;
    }).length;

    const lastMonthGaps = this.hands.filter(hand => {
      const handDate = new Date(hand.date_played);
      return handDate.getMonth() === lastMonth && 
             handDate.getFullYear() === lastYear && 
             hand.has_gap;
    }).length;

    const currentGapRate = this.handsThisMonth > 0 ? (this.gapsThisMonth / this.handsThisMonth) * 100 : 0;
    const lastGapRate = lastMonthHands > 0 ? (lastMonthGaps / lastMonthHands) * 100 : 0;
    
    this.monthlyImprovement = lastGapRate > 0 ? lastGapRate - currentGapRate : 0;
  }

  getStreetFromHand(hand: Hand): string {
    if (!hand.board_cards || hand.board_cards.length === 0) return 'preflop';
    if (hand.board_cards.length <= 5) return 'flop';
    if (hand.board_cards.length <= 7) return 'turn';
    return 'river';
  }

  goToHistory() {
    this.router.navigate(['/history']);
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        this.selectedFile = file;
        this.uploadMessage = `Arquivo selecionado: ${file.name}`;
      } else {
        this.uploadMessage = 'Por favor, selecione um arquivo .txt';
        this.selectedFile = null;
      }
    }
  }

  openFileDialog() {
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    fileInput?.click();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        this.selectedFile = file;
        this.uploadMessage = `Arquivo selecionado: ${file.name}`;
      } else {
        this.uploadMessage = 'Por favor, selecione um arquivo .txt';
        this.selectedFile = null;
      }
    }
  }

  uploadFile() {
    if (!this.selectedFile) {
      this.uploadMessage = 'Por favor, selecione um arquivo primeiro';
      return;
    }

    console.log('🚀 Iniciando upload...');
    this.isUploading = true;
    this.uploadMessage = '';

    // Forçar detecção de mudanças para garantir que o modal apareça
    this.cdr.detectChanges();

    // Simular progresso inicial para mostrar o modal imediatamente
    this.uploadService.progressSubject.next({
      status: 'starting',
      progress: 0,
      total_hands: 0,
      processed_hands: 0,
      current_hand: 'Iniciando upload...',
      message: 'Preparando para processar arquivo...',
      errors: [],
      completed: false,
      result: undefined
    });

    // Forçar detecção de mudanças novamente após enviar progresso
    setTimeout(() => {
      this.cdr.detectChanges();
      
      // Resetar componente de progresso se existir
      if (this.progressComponent) {
        console.log('🔄 Resetando componente de progresso');
        this.progressComponent.resetComponent();
      } else {
        console.log('⚠️ progressComponent não encontrado');
      }

      console.log('📤 Chamando uploadService.uploadFile...');
      this.uploadService.uploadFile(this.selectedFile!).subscribe({
        next: (response) => {
          console.log('📤 Upload iniciado:', response);
          console.log('🔍 Response completo:', JSON.stringify(response));
          
          // Iniciar tracking de progresso usando polling (mais confiável)
          if (response.upload_id) {
            console.log('🔄 Iniciando tracking de progresso para:', response.upload_id);
            this.uploadService.startProgressTracking(response.upload_id);
            console.log('✅ startProgressTracking chamado');
            
            // Escutar o progresso para definir isUploading como false quando completar
            this.uploadService.progress$.subscribe(progress => {
              if (progress && (progress.completed || progress.status === 'error')) {
                console.log('🎉 Progresso final detectado, definindo isUploading como false');
                this.isUploading = false;
              }
            });
          } else {
            console.log('⚠️ Nenhum upload_id recebido na resposta');
          }
          
          // NÃO definir isUploading como false aqui - deixar o polling controlar
          this.uploadMessage = 'Upload iniciado com sucesso!';
          this.selectedFile = null;
          
          console.log('✅ Upload iniciado, aguardando polling...');
          console.log('🔍 isUploadingInProgress:', this.isUploadingInProgress);
        },
        error: (error) => {
          this.isUploading = false;
          this.uploadMessage = 'Erro no upload: ' + (error.error?.detail || error.message);
          this.notificationService.error('Erro ao processar arquivo');
          console.error('❌ Erro no upload:', error);
        }
      });
    }, 100);
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  get totalHands(): number {
    return this.hands.length;
  }

  get gapsFound(): number {
    return this.hands.filter(hand => hand.has_gap).length;
  }

  get gapPercentage(): number {
    return this.totalHands > 0 ? (this.gapsFound / this.totalHands) * 100 : 0;
  }

  get recentHands(): Hand[] {
    return this.hands.slice(0, 10);
  }

  get positionStats(): Array<{position: string, count: number}> {
    const stats = new Map<string, number>();
    this.hands.forEach(hand => {
      const position = hand.hero_position || 'unknown';
      stats.set(position, (stats.get(position) || 0) + 1);
    });
    return Array.from(stats.entries()).map(([position, count]) => ({ position, count }));
  }

  get actionStats(): Array<{action: string, count: number}> {
    const stats = new Map<string, number>();
    this.hands.forEach(hand => {
      const action = hand.hero_action || 'unknown';
      stats.set(action, (stats.get(action) || 0) + 1);
    });
    return Array.from(stats.entries()).map(([action, count]) => ({ action, count }));
  }

  formatCards(cards: string): string {
    if (!cards) return '';
    return cards.replace(/([2-9TJQKA])([hdcs])/g, '$1$2 ').trim();
  }

  getCardClass(card: string): string {
    if (!card) return '';
    const suits = card.match(/[hdcs]/g);
    if (suits) {
      const suit = suits[0];
      if (suit === 'h' || suit === 'd') {
        return 'red-suit';
      } else {
        return 'black-suit';
      }
    }
    return '';
  }

  getPercentage(value: number, total: number): number {
    return total > 0 ? Math.round((value / total) * 100) : 0;
  }

  getPositionName(position: string): string {
    const positionNames: { [key: string]: string } = {
      'BTN': 'Button',
      'SB': 'Small Blind',
      'BB': 'Big Blind',
      'UTG': 'UTG',
      'UTG+1': 'UTG+1',
      'UTG+2': 'UTG+2',
      'MP': 'Middle Position',
      'MP+1': 'MP+1',
      'HJ': 'Hijack',
      'CO': 'Cutoff',
      'unknown': 'Desconhecida'
    };
    return positionNames[position] || position;
  }

  getActionName(action: string): string {
    const actionNames: { [key: string]: string } = {
      'fold': 'Fold',
      'call': 'Call',
      'raise': 'Raise',
      'bet': 'Bet',
      'check': 'Check',
      'all-in': 'All-in',
      'unknown': 'Desconhecida'
    };
    return actionNames[action] || action;
  }

  @ViewChild('progressComponent') progressComponent?: UploadProgressComponent;

  get isUploadingInProgress(): boolean {
    const hasProgress = this.uploadService.progressSubject.value !== null;
    const isUploading = this.isUploading;
    
    const shouldShow = isUploading || hasProgress;
    
    console.log('🔍 Modal Debug:', {
      isUploading,
      hasProgress,
      progressValue: this.uploadService.progressSubject.value,
      shouldShow
    });
    
    return shouldShow;
  }
}
