import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

interface User {
  id: number;
  name: string;
  email: string;
}

interface Hand {
  id: number;
  user_id: number;
  hand_text: string;
  analysis: any;
  gaps_found: any[];
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'GapHunter';
  
  // Auth state
  isAuthenticated = false;
  currentUser: User | null = null;
  authMode: 'login' | 'register' = 'login';
  
  // Form data
  loginData = { email: '', password: '' };
  registerData = { name: '', email: '', password: '' };
  
  // UI state
  isLoading = false;
  message = '';
  messageType: 'success' | 'error' = 'success';
  currentView: 'dashboard' | 'upload' | 'history' = 'dashboard';
  
  // Upload state
  isDragOver = false;
  uploadProgress = 0;
  
  // Data
  hands: Hand[] = [];
  stats = {
    totalHands: 0,
    totalGaps: 0,
    criticalGaps: 0
  };

  ngOnInit() {
    this.checkAuthStatus();
    if (this.isAuthenticated) {
      this.loadDashboardData();
    }
  }

  private checkAuthStatus() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      try {
        this.currentUser = JSON.parse(user);
        this.isAuthenticated = true;
      } catch (error) {
        this.logout();
      }
    }
  }

  async login() {
    if (!this.loginData.email || !this.loginData.password) {
      this.showMessage('Por favor, preencha todos os campos', 'error');
      return;
    }

    this.isLoading = true;
    this.message = '';

    try {
      const response = await fetch('https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.loginData)
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        this.currentUser = data.user;
        this.isAuthenticated = true;
        this.showMessage('Login realizado com sucesso!', 'success');
        this.loadDashboardData();
      } else {
        this.showMessage(data.detail || 'Erro ao fazer login', 'error');
      }
    } catch (error) {
      this.showMessage('Erro de conexão. Tente novamente.', 'error');
    } finally {
      this.isLoading = false;
    }
  }

  async register() {
    if (!this.registerData.name || !this.registerData.email || !this.registerData.password) {
      this.showMessage('Por favor, preencha todos os campos', 'error');
      return;
    }

    this.isLoading = true;
    this.message = '';

    try {
      const response = await fetch('https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.registerData)
      });

      const data = await response.json();

      if (response.ok) {
        this.showMessage('Conta criada com sucesso! Faça login.', 'success');
        this.authMode = 'login';
        this.registerData = { name: '', email: '', password: '' };
      } else {
        this.showMessage(data.detail || 'Erro ao criar conta', 'error');
      }
    } catch (error) {
      this.showMessage('Erro de conexão. Tente novamente.', 'error');
    } finally {
      this.isLoading = false;
    }
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.currentUser = null;
    this.isAuthenticated = false;
    this.currentView = 'dashboard';
    this.hands = [];
    this.stats = { totalHands: 0, totalGaps: 0, criticalGaps: 0 };
  }

  setView(view: 'dashboard' | 'upload' | 'history') {
    this.currentView = view;
    
    if (view === 'history') {
      this.loadHands();
    }
  }

  private showMessage(text: string, type: 'success' | 'error') {
    this.message = text;
    this.messageType = type;
    
    setTimeout(() => {
      this.message = '';
    }, 5000);
  }

  private async loadDashboardData() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api/hands/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        this.stats = await response.json();
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  }

  private async loadHands() {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api/hands', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        this.hands = data.hands || [];
      }
    } catch (error) {
      console.error('Erro ao carregar mãos:', error);
    }
  }

  // Upload methods
  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.uploadFile(files[0]);
    }
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.uploadFile(file);
    }
  }

  private async uploadFile(file: File) {
    if (!file.name.endsWith('.txt')) {
      this.showMessage('Por favor, selecione um arquivo .txt', 'error');
      return;
    }

    this.uploadProgress = 0;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api/hands/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      this.uploadProgress = 100;

      if (response.ok) {
        const data = await response.json();
        this.showMessage('Arquivo enviado e analisado com sucesso!', 'success');
        this.loadDashboardData(); // Atualizar estatísticas
        
        setTimeout(() => {
          this.uploadProgress = 0;
        }, 2000);
      } else {
        const error = await response.json();
        this.showMessage(error.detail || 'Erro ao enviar arquivo', 'error');
        this.uploadProgress = 0;
      }
    } catch (error) {
      this.showMessage('Erro de conexão. Tente novamente.', 'error');
      this.uploadProgress = 0;
    }
  }
}

