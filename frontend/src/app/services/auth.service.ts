import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';

export interface User {
  id: number;
  username: string;
  full_name: string;
  nickname: string;
  email: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  full_name: string;
  nickname: string;
  email: string;
  password: string;
  // Informações específicas de poker
  poker_experience?: string;
  preferred_games?: string;
  main_stakes?: string;
  poker_goals?: string;
  country?: string;
  timezone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Verificar se há token salvo no localStorage
    const token = this.getToken();
    if (token) {
      this.validateToken();
    }
  }

  private validateToken(): void {
    // Fazer uma requisição simples para validar o token
    this.http.get(`${this.apiUrl}/auth/me`).subscribe({
      next: (user: any) => {
        this.currentUserSubject.next(user);
      },
      error: () => {
        // Token inválido, remover
        this.logout();
      }
    });
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    return this.http.post<Token>(`${this.apiUrl}/auth/login`, formData)
      .pipe(
        switchMap(tokenResponse => {
          // Salvar token
          this.setToken(tokenResponse.access_token);
          
          // Buscar dados do usuário
          return this.http.get<User>(`${this.apiUrl}/auth/me`, {
            headers: { Authorization: `Bearer ${tokenResponse.access_token}` }
          }).pipe(
            map(user => {
              this.currentUserSubject.next(user);
              return {
                access_token: tokenResponse.access_token,
                token_type: tokenResponse.token_type,
                user: user
              };
            })
          );
        }),
        catchError(this.handleError)
      );
  }

  register(userData: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<Token>(`${this.apiUrl}/auth/register`, userData)
      .pipe(
        switchMap(tokenResponse => {
          // Salvar token
          this.setToken(tokenResponse.access_token);
          
          // Buscar dados do usuário
          return this.http.get<User>(`${this.apiUrl}/auth/me`, {
            headers: { Authorization: `Bearer ${tokenResponse.access_token}` }
          }).pipe(
            map(user => {
              this.currentUserSubject.next(user);
              return {
                access_token: tokenResponse.access_token,
                token_type: tokenResponse.token_type,
                user: user
              };
            })
          );
        }),
        catchError(this.handleError)
      );
  }

  logout(): void {
    localStorage.removeItem('token');
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  private setToken(token: string): void {
    localStorage.setItem('token', token);
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token;
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Erro desconhecido';
    
    if (error.error instanceof ErrorEvent) {
      // Erro do lado do cliente
      errorMessage = `Erro: ${error.error.message}`;
    } else {
      // Erro do lado do servidor
      if (error.error && error.error.detail) {
        errorMessage = error.error.detail;
      } else if (error.error && typeof error.error === 'string') {
        errorMessage = error.error;
      } else if (error.message) {
        errorMessage = error.message;
      } else {
        errorMessage = `Erro ${error.status}: ${error.statusText}`;
      }
    }
    
    return throwError(() => errorMessage);
  }
}

