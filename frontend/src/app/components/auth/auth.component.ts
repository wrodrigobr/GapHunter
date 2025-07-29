import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, LoginRequest, RegisterRequest } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss'
})
export class AuthComponent {
  isLoginMode = true;
  isLoading = false;

  loginData: LoginRequest = {
    email: '',
    password: ''
  };

  registerData: RegisterRequest = {
    username: '',
    full_name: '',
    email: '',
    password: '',
    poker_experience: '',
    preferred_games: '',
    main_stakes: '',
    poker_goals: '',
    country: '',
    timezone: ''
  };

  constructor(
    private authService: AuthService,
    private router: Router,
    private notificationService: NotificationService
  ) {}

  toggleMode() {
    this.isLoginMode = !this.isLoginMode;
  }

  onLogin() {
    if (!this.loginData.email || !this.loginData.password) {
      this.notificationService.warning('Campos obrigatórios', 'Por favor, preencha todos os campos');
      return;
    }

    this.isLoading = true;

    this.authService.login(this.loginData).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.notificationService.success('Login realizado!', `Bem-vindo de volta, ${response.user.full_name}`);
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.isLoading = false;
        this.notificationService.error('Erro no login', error);
      }
    });
  }

  onRegister() {
    if (!this.registerData.username || !this.registerData.full_name || !this.registerData.email || !this.registerData.password) {
      this.notificationService.warning('Campos obrigatórios', 'Por favor, preencha todos os campos obrigatórios');
      return;
    }

    if (this.registerData.password.length < 6) {
      this.notificationService.warning('Senha muito curta', 'A senha deve ter pelo menos 6 caracteres');
      return;
    }

    this.isLoading = true;

    this.authService.register(this.registerData).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.notificationService.success('Conta criada!', `Bem-vindo ao GapHunter, ${response.user.full_name}`);
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.isLoading = false;
        this.notificationService.error('Erro no registro', error);
      }
    });
  }
}

