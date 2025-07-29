import { Routes } from '@angular/router';
import { AuthComponent } from './components/auth/auth.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { HistoryComponent } from './components/history/history.component';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/auth', pathMatch: 'full' },
  { path: 'auth', component: AuthComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'history', component: HistoryComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: '/auth' }
];
