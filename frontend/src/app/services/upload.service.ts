import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, interval } from 'rxjs';
import { switchMap, takeWhile, finalize, timeout, catchError, tap } from 'rxjs/operators';

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
  //private apiUrl = 'https://ghunter-backend-djfcaycjd5eeeahu.brazilsouth-01.azurewebsites.net/api';
  public progressSubject = new BehaviorSubject<UploadProgress | null>(null);
  public progress$ = this.progressSubject.asObservable();
  public uploadCompletedSubject = new BehaviorSubject<boolean>(false);
  public uploadCompleted$ = this.uploadCompletedSubject.asObservable();

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<UploadStartResponse> {
    const formData = new FormData();
    formData.append('file', file);

    console.log('📤 Enviando arquivo para upload:', file.name, 'Tamanho:', file.size, 'bytes');
    return this.http.post<UploadStartResponse>(`${this.apiUrl}/upload/upload-async`, formData).pipe(
      timeout(120000), // 2 minutos de timeout
      catchError(error => {
        console.error('❌ Erro no upload:', error);
        throw error;
      })
    );
  }

  startProgressTracking(uploadId: string): void {
    console.log('🚀 startProgressTracking iniciado para:', uploadId);
    
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

    console.log('🔄 Iniciando tracking de progresso para:', uploadId);
    
    // Polling do progresso a cada segundo
    interval(1000).pipe(
      tap(() => console.log('⏰ Interval executado, fazendo requisição...')),
      switchMap(() => {
        console.log('📡 Fazendo requisição de progresso para:', uploadId);
        return this.getProgress(uploadId);
      }),
      takeWhile((progress) => {
        console.log('📊 Progresso recebido:', progress);
        const shouldContinue = !progress.completed && progress.status !== 'error';
        console.log('🔄 Deve continuar polling?', shouldContinue);
        return shouldContinue;
      }, true),
      finalize(() => {
        console.log('✅ Upload finalizado, parando polling');
        this.uploadCompletedSubject.next(true);
      })
    ).subscribe({
      next: (progress) => {
        console.log('📈 Atualizando progresso:', progress);
        this.progressSubject.next(progress);
        
        // Verificar se completou aqui também
        if (progress.completed || progress.status === 'error') {
          console.log('🎯 Progresso final detectado no next, emitindo completed');
          this.uploadCompletedSubject.next(true);
        }
      },
      error: (error) => {
        console.error('❌ Erro ao obter progresso:', error);
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
        console.log('🎯 Erro detectado, emitindo completed');
        this.uploadCompletedSubject.next(true);
      }
    });
  }

  private getProgress(uploadId: string): Observable<UploadProgress> {
    const url = `${this.apiUrl}/upload/upload-progress/${uploadId}`;
    console.log('🌐 Fazendo GET para:', url);
    return this.http.get<UploadProgress>(url);
  }

  // Método usando Server-Sent Events (mais eficiente)
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
        console.log('📊 Progresso recebido:', progress);
        this.progressSubject.next(progress);
        
        // Fechar conexão quando completar
        if (progress.completed || progress.status === 'error') {
          console.log('✅ Upload concluído ou erro, fechando conexão SSE');
          eventSource.close();
          // Não limpar automaticamente - deixar o componente controlar
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
    console.log('🧹 Limpando progresso manualmente');
    this.progressSubject.next(null);
  }
}

