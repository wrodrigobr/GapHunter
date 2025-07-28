from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import statistics

from app.models.tournament import Tournament, PerformanceStats
from app.models.user import User

class PerformanceAnalysisService:
    def __init__(self):
        pass

    def calculate_roi(self, buy_in: float, prize: float) -> float:
        """Calcula ROI de um torneio específico"""
        if buy_in <= 0:
            return 0.0
        return ((prize - buy_in) / buy_in) * 100

    def parse_tournament_from_hand_history(self, hand_history: str) -> Dict:
        """Extrai informações do torneio do hand history"""
        lines = hand_history.strip().split('\n')
        tournament_info = {}
        
        for line in lines:
            if 'Tournament #' in line:
                # PokerStars Hand #123456789: Tournament #987654321, $5.00+$0.50 USD
                parts = line.split('Tournament #')
                if len(parts) > 1:
                    tournament_part = parts[1].split(',')
                    tournament_info['tournament_id'] = tournament_part[0].strip()
                    
                    # Extrair buy-in
                    if '$' in line:
                        buy_in_part = line.split('$')[1].split(' ')[0]
                        try:
                            # Formato: $5.00+$0.50
                            if '+$' in buy_in_part:
                                main_buy_in = float(buy_in_part.split('+$')[0])
                                fee = float(buy_in_part.split('+$')[1])
                                tournament_info['buy_in'] = main_buy_in + fee
                            else:
                                tournament_info['buy_in'] = float(buy_in_part)
                        except:
                            tournament_info['buy_in'] = 0.0
                
                # Extrair data
                if ' - ' in line:
                    date_part = line.split(' - ')[-1].strip()
                    try:
                        tournament_info['date_played'] = datetime.strptime(
                            date_part, "%Y/%m/%d %H:%M:%S ET"
                        )
                    except:
                        tournament_info['date_played'] = datetime.now()
                        
                break
        
        return tournament_info

    def add_tournament_result(self, db: Session, user_id: int, tournament_data: Dict) -> Tournament:
        """Adiciona resultado de torneio"""
        
        # Verificar se torneio já existe
        existing = db.query(Tournament).filter(
            and_(
                Tournament.user_id == user_id,
                Tournament.tournament_id == tournament_data.get('tournament_id')
            )
        ).first()
        
        if existing:
            return existing
        
        # Criar novo torneio
        tournament = Tournament(
            user_id=user_id,
            tournament_id=tournament_data.get('tournament_id', ''),
            name=tournament_data.get('name', 'Tournament'),
            buy_in=tournament_data.get('buy_in', 0.0),
            prize_pool=tournament_data.get('prize_pool'),
            players_count=tournament_data.get('players_count'),
            position=tournament_data.get('position'),
            prize=tournament_data.get('prize', 0.0),
            date_played=tournament_data.get('date_played', datetime.now()),
            platform=tournament_data.get('platform', 'PokerStars')
        )
        
        # Calcular ROI e ITM
        tournament.roi = self.calculate_roi(tournament.buy_in, tournament.prize)
        tournament.is_itm = tournament.prize > 0
        
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
        
        # Atualizar estatísticas de performance
        self.update_performance_stats(db, user_id)
        
        return tournament

    def get_user_tournaments(self, db: Session, user_id: int, limit: int = 50) -> List[Tournament]:
        """Obtém torneios do usuário"""
        return db.query(Tournament).filter(
            Tournament.user_id == user_id
        ).order_by(desc(Tournament.date_played)).limit(limit).all()

    def calculate_performance_stats(self, db: Session, user_id: int, days_back: int = 30) -> Dict:
        """Calcula estatísticas de performance"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        tournaments = db.query(Tournament).filter(
            and_(
                Tournament.user_id == user_id,
                Tournament.date_played >= cutoff_date
            )
        ).all()
        
        if not tournaments:
            return self._empty_stats()
        
        # Estatísticas básicas
        total_buy_ins = sum(t.buy_in for t in tournaments)
        total_prizes = sum(t.prize for t in tournaments)
        net_profit = total_prizes - total_buy_ins
        roi_percentage = (net_profit / total_buy_ins * 100) if total_buy_ins > 0 else 0
        
        # Estatísticas de ITM
        itm_tournaments = [t for t in tournaments if t.is_itm]
        itm_count = len(itm_tournaments)
        itm_percentage = (itm_count / len(tournaments) * 100) if tournaments else 0
        
        # Estatísticas de posicionamento
        positions = [t.position for t in tournaments if t.position]
        avg_finish = statistics.mean(positions) if positions else 0
        best_finish = min(positions) if positions else 0
        worst_finish = max(positions) if positions else 0
        
        # Estatísticas financeiras
        avg_buy_in = statistics.mean([t.buy_in for t in tournaments]) if tournaments else 0
        biggest_win = max([t.prize for t in tournaments]) if tournaments else 0
        biggest_loss = max([t.buy_in for t in tournaments if t.prize == 0]) if tournaments else 0
        
        return {
            'period_days': days_back,
            'tournaments_played': len(tournaments),
            'total_buy_ins': round(total_buy_ins, 2),
            'total_prizes': round(total_prizes, 2),
            'net_profit': round(net_profit, 2),
            'roi_percentage': round(roi_percentage, 2),
            'itm_count': itm_count,
            'itm_percentage': round(itm_percentage, 2),
            'avg_finish_position': round(avg_finish, 1) if avg_finish else 0,
            'best_finish': best_finish,
            'worst_finish': worst_finish,
            'avg_buy_in': round(avg_buy_in, 2),
            'biggest_win': round(biggest_win, 2),
            'biggest_loss': round(biggest_loss, 2),
            'profit_per_tournament': round(net_profit / len(tournaments), 2) if tournaments else 0
        }

    def update_performance_stats(self, db: Session, user_id: int):
        """Atualiza estatísticas de performance no banco"""
        
        # Calcular stats para diferentes períodos
        periods = [7, 30, 90, 365]
        
        for days in periods:
            stats = self.calculate_performance_stats(db, user_id, days)
            
            # Verificar se já existe registro para este período
            existing = db.query(PerformanceStats).filter(
                and_(
                    PerformanceStats.user_id == user_id,
                    PerformanceStats.period_start >= datetime.utcnow() - timedelta(days=days)
                )
            ).first()
            
            if existing:
                # Atualizar existente
                for key, value in stats.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Criar novo
                performance_stats = PerformanceStats(
                    user_id=user_id,
                    period_start=datetime.utcnow() - timedelta(days=days),
                    period_end=datetime.utcnow(),
                    **{k: v for k, v in stats.items() if hasattr(PerformanceStats, k)}
                )
                db.add(performance_stats)
        
        db.commit()

    def get_roi_chart_data(self, db: Session, user_id: int, days_back: int = 30) -> List[Dict]:
        """Obtém dados para gráfico de ROI"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        tournaments = db.query(Tournament).filter(
            and_(
                Tournament.user_id == user_id,
                Tournament.date_played >= cutoff_date
            )
        ).order_by(Tournament.date_played).all()
        
        if not tournaments:
            return []
        
        # Calcular ROI cumulativo
        cumulative_buy_ins = 0
        cumulative_prizes = 0
        chart_data = []
        
        for tournament in tournaments:
            cumulative_buy_ins += tournament.buy_in
            cumulative_prizes += tournament.prize
            
            cumulative_roi = ((cumulative_prizes - cumulative_buy_ins) / cumulative_buy_ins * 100) if cumulative_buy_ins > 0 else 0
            
            chart_data.append({
                'date': tournament.date_played.strftime('%Y-%m-%d'),
                'roi': round(cumulative_roi, 2),
                'profit': round(cumulative_prizes - cumulative_buy_ins, 2),
                'tournaments': len(chart_data) + 1
            })
        
        return chart_data

    def _empty_stats(self) -> Dict:
        """Retorna estatísticas vazias"""
        return {
            'period_days': 0,
            'tournaments_played': 0,
            'total_buy_ins': 0.0,
            'total_prizes': 0.0,
            'net_profit': 0.0,
            'roi_percentage': 0.0,
            'itm_count': 0,
            'itm_percentage': 0.0,
            'avg_finish_position': 0,
            'best_finish': 0,
            'worst_finish': 0,
            'avg_buy_in': 0.0,
            'biggest_win': 0.0,
            'biggest_loss': 0.0,
            'profit_per_tournament': 0.0
        }

