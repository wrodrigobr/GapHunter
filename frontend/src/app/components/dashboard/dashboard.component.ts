import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';
import { ApiService, Hand } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
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
      this.selectedFile = file;
      this.uploadMessage = '';
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
      this.selectedFile = files[0];
      this.uploadMessage = '';
    }
  }

  uploadFile() {
    if (!this.selectedFile) {
      this.uploadMessage = 'Por favor, selecione um arquivo';
      return;
    }

    this.isUploading = true;
    this.uploadMessage = '';

    this.apiService.uploadHand(this.selectedFile).subscribe({
      next: (response) => {
        this.isUploading = false;
        this.uploadMessage = `Sucesso! ${response.gaps_found} gaps encontrados`;
        this.selectedFile = null;
        this.loadHands(); // Recarregar lista de mãos
      },
      error: (error) => {
        this.isUploading = false;
        this.uploadMessage = error;
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

