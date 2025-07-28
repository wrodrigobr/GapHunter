import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Hand {
  id: number;
  filename: string;
  content: string;
  gaps_count: number;
  created_at: string;
  user_id: number;
}

export interface Gap {
  id: number;
  hand_id: number;
  gap_type: string;
  description: string;
  severity: string;
  recommendation: string;
}

export interface UploadResponse {
  message: string;
  hand_id: number;
  gaps_found: number;
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

  // Listar mãos do usuário
  getUserHands(): Observable<Hand[]> {
    return this.http.get<Hand[]>(`${this.apiUrl}/hands/`)
      .pipe(catchError(this.handleError));
  }

  // Obter detalhes de uma mão específica
  getHand(handId: number): Observable<Hand> {
    return this.http.get<Hand>(`${this.apiUrl}/hands/${handId}`)
      .pipe(catchError(this.handleError));
  }

  // Obter gaps de uma mão
  getHandGaps(handId: number): Observable<Gap[]> {
    return this.http.get<Gap[]>(`${this.apiUrl}/hands/${handId}/gaps`)
      .pipe(catchError(this.handleError));
  }

  // Verificar status da API
  getApiStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/`)
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

