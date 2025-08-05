import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { UploadService, UploadProgress } from '../../services/upload.service';

@Component({
  selector: 'app-upload-progress',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="upload-progress-overlay">
      <div class="upload-progress-modal">
        <div class="progress-header">
          <h3>
            <i class="fas fa-upload"></i>
            Analisando Hand History
          </h3>
          <div class="status-badge" [ngClass]="getStatusClass()">
            {{ getStatusText() }}
          </div>
        </div>

        <div class="progress-content">
          <!-- Barra de Progresso Principal -->
          <div class="progress-bar-container">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                [style.width.%]="progress?.progress || 0"
                [ngClass]="getProgressClass()">
              </div>
            </div>
            <div class="progress-text">
              {{ progress?.progress || 0 }}%
            </div>
          </div>

          <!-- Informações Detalhadas -->
          <div class="progress-details" *ngIf="progress">
            <div class="detail-row">
              <span class="label">Status:</span>
              <span class="value">{{ progress.message }}</span>
            </div>
            
            <div class="detail-row" *ngIf="progress.total_hands > 0">
              <span class="label">Progresso:</span>
              <span class="value">
                {{ progress.processed_hands }} / {{ progress.total_hands }} mãos
              </span>
            </div>
            
            <div class="detail-row" *ngIf="progress.current_hand">
              <span class="label">Processando:</span>
              <span class="value">{{ progress.current_hand }}</span>
            </div>
          </div>

          <!-- Resultado Final -->
          <div *ngIf="progress?.completed && progress?.result" class="result-summary">
            <div class="result-card success">
              <i class="fas fa-check-circle"></i>
              <div class="result-content">
                <h4>Upload Concluído!</h4>
                <p>
                  <strong>{{ progress?.result?.hands_processed || 0 }}</strong> mãos processadas
                  <span *ngIf="(progress?.result?.duplicates_skipped || 0) > 0">
                    ({{ progress?.result?.duplicates_skipped || 0 }} duplicatas ignoradas)
                  </span>
                </p>
              </div>
            </div>
          </div>

          <!-- Erros -->
          <div *ngIf="(progress?.errors?.length || 0) > 0" class="errors-section">
            <h4><i class="fas fa-exclamation-triangle"></i> Avisos:</h4>
            <ul class="error-list">
              <li *ngFor="let error of progress?.errors || []">{{ error }}</li>
            </ul>
          </div>

          <!-- Botões de Ação -->
          <div class="action-buttons">
            <button 
              *ngIf="progress?.completed || progress?.status === 'error'"
              class="btn btn-primary"
              (click)="closeProgress()">
              <i class="fas fa-times"></i>
              Fechar
            </button>
            
            <button 
              *ngIf="!progress?.completed && progress?.status !== 'error'"
              class="btn btn-secondary"
              (click)="cancelUpload()"
              disabled>
              <i class="fas fa-stop"></i>
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./upload-progress.component.scss']
})
export class UploadProgressComponent implements OnInit, OnDestroy {
  progress: UploadProgress | null = null;
  isClosed = false;
  private subscription?: Subscription;
  private autoCloseTimeout?: any;

  constructor(
    private uploadService: UploadService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.subscription = this.uploadService.progress$.subscribe(
      progress => {
        console.log('📊 Progresso atualizado no componente:', progress);
        console.log('🔍 Estado atual - isClosed:', this.isClosed, 'progress:', this.progress);
        
        // Se o modal foi fechado, não reabrir
        if (this.isClosed) {
          console.log('🚫 Modal fechado, ignorando atualizações');
          return;
        }
        
        // Atualizar progresso (mesmo se for null)
        this.progress = progress;
        console.log('✅ Progresso atualizado para:', this.progress);
        
        // Forçar detecção de mudanças
        this.cdr.detectChanges();
        
        // Auto-close modal when completed or error
        if (progress && (progress.completed || progress.status === 'error')) {
          console.log('🔄 Auto-fechando modal após conclusão/erro');
          
          // Limpar timeout anterior se existir
          if (this.autoCloseTimeout) {
            clearTimeout(this.autoCloseTimeout);
          }
          
          // Auto-close após 3 segundos
          this.autoCloseTimeout = setTimeout(() => {
            console.log('⏰ Timeout executado - fechando modal automaticamente');
            this.closeProgress();
          }, 3000);
        }
      }
    );
  }

  ngOnDestroy() {
    this.subscription?.unsubscribe();
    if (this.autoCloseTimeout) {
      clearTimeout(this.autoCloseTimeout);
    }
  }

  getStatusClass(): string {
    if (!this.progress) return '';
    
    switch (this.progress.status) {
      case 'completed': return 'status-success';
      case 'error': return 'status-error';
      case 'processing': return 'status-processing';
      default: return 'status-info';
    }
  }

  getStatusText(): string {
    if (!this.progress) return '';
    
    switch (this.progress.status) {
      case 'starting': return 'Iniciando';
      case 'reading_file': return 'Lendo Arquivo';
      case 'parsing': return 'Analisando';
      case 'processing': return 'Processando';
      case 'completed': return 'Concluído';
      case 'error': return 'Erro';
      default: return 'Processando';
    }
  }

  getProgressClass(): string {
    if (!this.progress) return '';
    
    switch (this.progress.status) {
      case 'completed': return 'progress-success';
      case 'error': return 'progress-error';
      default: return 'progress-active';
    }
  }

  closeProgress() {
    console.log('🔒 Fechando modal de progresso');
    console.log('🔍 Estado antes de fechar - isClosed:', this.isClosed, 'progress:', this.progress);
    
    // Limpar timeout se existir
    if (this.autoCloseTimeout) {
      clearTimeout(this.autoCloseTimeout);
      this.autoCloseTimeout = undefined;
    }
    
    this.isClosed = true;
    this.uploadService.clearProgress();
    this.progress = null;
    
    // Forçar detecção de mudanças para atualizar o template
    this.cdr.detectChanges();
    
    console.log('🔍 Estado após fechar - isClosed:', this.isClosed, 'progress:', this.progress);
    console.log('✅ Modal fechado com sucesso');
  }

  // Método para resetar o componente quando iniciar novo upload
  resetComponent() {
    console.log('🔄 Resetando componente de progresso');
    
    // Limpar timeout se existir
    if (this.autoCloseTimeout) {
      clearTimeout(this.autoCloseTimeout);
      this.autoCloseTimeout = undefined;
    }
    
    this.isClosed = false;
    this.progress = null;
    
    // Forçar detecção de mudanças para atualizar o template
    this.cdr.detectChanges();
    
    console.log('✅ Componente resetado - isClosed:', this.isClosed, 'progress:', this.progress);
  }

  cancelUpload() {
    // TODO: Implementar cancelamento
    console.log('Cancelamento não implementado ainda');
  }
}

