import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Hand {
  id: number;
  hand_id: string;
  hero_position?: string;
  hero_cards?: string;
  hero_action?: string;
  date_played: string;
  ai_analysis?: string;
  has_gap?: boolean;
  created_at: string;
  pokerstars_tournament_id?: string;
  table_name?: string;
  hero_name?: string;
  pot_size?: number;
  bet_amount?: number;
  board_cards?: string;
}

export interface UserStats {
  total_hands: number;
  gaps_found: number;
  gap_percentage: number;
  position_stats: Array<{position: string, count: number}>;
  action_stats: Array<{action: string, count: number}>;
  recent_hands: Hand[];
}

export interface UploadResponse {
  message: string;
  hands_processed: number;
  hands: Hand[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api';

  constructor(private http: HttpClient) {}

  // Upload de hand history
  uploadHand(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${this.apiUrl}/hands/upload`, formData)
      .pipe(catchError(this.handleError));
  }

  // Obter estatísticas do usuário
  getUserStats(): Observable<UserStats> {
    return this.http.get<UserStats>(`${this.apiUrl}/hands/stats`)
      .pipe(catchError(this.handleError));
  }

  // Listar mãos do usuário
  getUserHands(skip: number = 0, limit: number = 50): Observable<Hand[]> {
    return this.http.get<Hand[]>(`${this.apiUrl}/hands/history/my-hands?skip=${skip}&limit=${limit}`)
      .pipe(catchError(this.handleError));
  }

  // Obter detalhes de uma mão específica
  getHand(handId: number): Observable<Hand> {
    return this.http.get<Hand>(`${this.apiUrl}/hands/history/my-hands/${handId}`)
      .pipe(catchError(this.handleError));
  }

  // Deletar uma mão
  deleteHand(handId: number): Observable<{message: string}> {
    return this.http.delete<{message: string}>(`${this.apiUrl}/hands/history/my-hands/${handId}`)
      .pipe(catchError(this.handleError));
  }

  // Verificar status da API
  getApiStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/`)
      .pipe(catchError(this.handleError));
  }

  // Histórico de mãos com filtros
  getMyHands(params: any): Observable<Hand[]> {
    const queryParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key].toString());
      }
    });

    return this.http.get<Hand[]>(`${this.apiUrl}/hands/history/my-hands?${queryParams}`)
      .pipe(catchError(this.handleError));
  }

  // Contagem de mãos com filtros
  getMyHandsCount(filters: any): Observable<{total: number}> {
    const queryParams = new URLSearchParams();
    
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
        queryParams.append(key, filters[key].toString());
      }
    });

    return this.http.get<{total: number}>(`${this.apiUrl}/hands/history/my-hands/count?${queryParams}`)
      .pipe(catchError(this.handleError));
  }

  // Opções de filtros
  getFilterOptions(): Observable<any> {
    return this.http.get(`${this.apiUrl}/hands/history/filters/options`)
      .pipe(catchError(this.handleError));
  }

  // Obter dados de replay da mão
  getHandReplay(handId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/hands/replay/${handId}`)
      .pipe(catchError(this.handleError));
  }

  // Analisar ação específica
  analyzeSpecificAction(handId: number, actionData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/hands/replay/${handId}/analyze-action`, actionData)
      .pipe(catchError(this.handleError));
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

