import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { inject } from '@angular/core';
import { HttpRequest, HttpHandlerFn } from '@angular/common/http';

import { routes } from './app.routes';
import { AuthService } from './services/auth.service';

// Interceptor funcional para Angular 17
export function authInterceptor(req: HttpRequest<unknown>, next: HttpHandlerFn) {
  const authService = inject(AuthService);
  const token = authService.getToken();
  
  console.log('🔐 Interceptor executado para:', req.url);
  console.log('🎫 Token encontrado:', token ? 'SIM' : 'NÃO');
  
  if (token) {
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    console.log('✅ Header Authorization adicionado');
    return next(authReq);
  }
  
  console.log('❌ Requisição sem token');
  return next(req);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }), 
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor]))
  ]
};