import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, interval } from 'rxjs';
import { switchMap, takeWhile, finalize } from 'rxjs/operators';

export interface UploadProgress {
  status: 'starting' | 'reading_file' | 'parsing' | 'processing' | 'completed' | 'error';
  progress: number;
  total_hands: number;
  processed_hands: number;
  current_hand: string;
  message: string;
  errors: string[];
  completed: boolean;
  result?: {
    hands_processed: number;
    total_found: number;
    duplicates_skipped: number;
  };
}

export interface UploadStartResponse {
  upload_id: string;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = 'http://localhost:8000/api';
  public progressSubject = new BehaviorSubject<UploadProgress | null>(null);
  public progress$ = this.progressSubject.asObservable();

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<UploadStartResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadStartResponse>(`${this.apiUrl}/upload/upload-async`, formData);
  }

  startProgressTracking(uploadId: string): void {
    // Resetar progresso
    this.progressSubject.next({
      status: 'starting',
      progress: 0,
      total_hands: 0,
      processed_hands: 0,
      current_hand: '',
      message: 'Iniciando...',
      errors: [],
      completed: false
    });

    // Polling do progresso a cada segundo
    interval(1000).pipe(
      switchMap(() => this.getProgress(uploadId)),
      takeWhile((progress) => !progress.completed && progress.status !== 'error', true),
      finalize(() => {
        // Limpar após 5 segundos quando completar
        setTimeout(() => {
          this.progressSubject.next(null);
        }, 5000);
      })
    ).subscribe({
      next: (progress) => {
        this.progressSubject.next(progress);
      },
      error: (error) => {
        console.error('Erro ao obter progresso:', error);
        this.progressSubject.next({
          status: 'error',
          progress: 0,
          total_hands: 0,
          processed_hands: 0,
          current_hand: '',
          message: 'Erro ao obter progresso do upload',
          errors: [error.message || 'Erro desconhecido'],
          completed: false
        });
      }
    });
  }

  private getProgress(uploadId: string): Observable<UploadProgress> {
    return this.http.get<UploadProgress>(`${this.apiUrl}/upload/upload-progress/${uploadId}`);
  }

  // Método alternativo usando Server-Sent Events (mais eficiente)
  startProgressTrackingSSE(uploadId: string): void {
    this.progressSubject.next({
      status: 'starting',
      progress: 0,
      total_hands: 0,
      processed_hands: 0,
      current_hand: '',
      message: 'Iniciando...',
      errors: [],
      completed: false
    });

    const eventSource = new EventSource(`${this.apiUrl}/upload/upload-stream/${uploadId}`);
    
    eventSource.onmessage = (event) => {
      try {
        const progress: UploadProgress = JSON.parse(event.data);
        this.progressSubject.next(progress);
        
        // Fechar conexão quando completar
        if (progress.completed || progress.status === 'error') {
          eventSource.close();
          
          // Limpar após 5 segundos
          setTimeout(() => {
            this.progressSubject.next(null);
          }, 5000);
        }
      } catch (error) {
        console.error('Erro ao parsear progresso SSE:', error);
        eventSource.close();
      }
    };

    eventSource.onerror = (error) => {
      console.error('Erro na conexão SSE:', error);
      eventSource.close();
      
      this.progressSubject.next({
        status: 'error',
        progress: 0,
        total_hands: 0,
        processed_hands: 0,
        current_hand: '',
        message: 'Erro na conexão de progresso',
        errors: ['Falha na conexão com servidor'],
        completed: false
      });
    };
  }

  clearProgress(): void {
    this.progressSubject.next(null);
  }
}

