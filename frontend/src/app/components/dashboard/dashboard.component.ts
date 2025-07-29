import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';
import { ApiService, Hand } from '../../services/api.service';
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
  currentUser: User | null = null;
  hands: Hand[] = [];
  isLoading = true;
  errorMessage = '';
  selectedFile: File | null = null;
  isUploading = false;
  uploadMessage = '';

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private uploadService: UploadService,
    private notificationService: NotificationService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (!user) {
        this.router.navigate(['/auth']);
      }
    });

    this.loadHands();
  }

  loadHands() {
    this.isLoading = true;
    this.apiService.getUserHands().subscribe({
      next: (hands) => {
        this.hands = hands;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = error;
        this.isLoading = false;
      }
    });
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
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    
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
      this.notificationService.error('Por favor, selecione um arquivo');
      return;
    }

    console.log('📁 Iniciando upload do arquivo:', this.selectedFile.name);

    this.isUploading = true;
    this.uploadMessage = 'Iniciando upload...';

    this.uploadService.uploadFile(this.selectedFile).subscribe({
      next: (response) => {
        console.log('✅ Upload iniciado:', response);
        this.notificationService.info('Upload iniciado! Acompanhe o progresso.');
        
        // Iniciar tracking de progresso usando Server-Sent Events
        this.uploadService.startProgressTrackingSSE(response.upload_id);
        
        // Limpar seleção de arquivo
        this.selectedFile = null;
        this.uploadMessage = '';
        this.isUploading = false;
        
        // Escutar conclusão do upload
        this.uploadService.progress$.subscribe(progress => {
          if (progress?.completed && progress.result) {
            this.notificationService.success(
              `Upload concluído! ${progress.result.hands_processed} mãos processadas.`
            );
            
            // Recarregar dados
            this.loadHands();
          } else if (progress?.status === 'error') {
            this.notificationService.error(
              progress.message || 'Erro durante o upload'
            );
          }
        });
      },
      error: (error) => {
        console.error('❌ Erro no upload:', error);
        this.isUploading = false;
        this.uploadMessage = '';
        
        let errorMessage = 'Erro ao fazer upload do arquivo';
        
        if (error.status === 0) {
          errorMessage = 'Erro de conexão. Verifique sua internet e tente novamente.';
        } else if (error.error?.detail) {
          errorMessage = error.error.detail;
        }
        
        this.notificationService.error(errorMessage);
      }
    });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getTotalGaps(): number {
    return this.hands.reduce((total, hand) => total + hand.gaps_count, 0);
  }

  getAverageGaps(): string {
    if (this.hands.length === 0) return '0.0';
    const average = this.getTotalGaps() / this.hands.length;
    return average.toFixed(1);
  }
}

