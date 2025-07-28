from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

from app.models.database import get_db
from app.models.user import User
from app.models.tournament import Tournament
from app.services.auth import get_current_active_user
from app.services.performance_service import PerformanceAnalysisService

router = APIRouter()
performance_service = PerformanceAnalysisService()

class TournamentCreate(BaseModel):
    tournament_id: str
    name: str = "Tournament"
    buy_in: float
    prize: float = 0.0
    position: int = None
    players_count: int = None
    date_played: str = None

class TournamentResponse(BaseModel):
    id: int
    tournament_id: str
    name: str
    buy_in: float
    prize: float
    position: int = None
    roi: float
    is_itm: bool
    date_played: str
    platform: str

    class Config:
        from_attributes = True

@router.get("/stats")
async def get_performance_stats(
    days_back: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de performance do usuário"""
    stats = performance_service.calculate_performance_stats(db, current_user.id, days_back)
    return {
        "user_id": current_user.id,
        "period_analyzed": f"{days_back} days",
        "stats": stats
    }

@router.get("/tournaments")
async def get_tournaments(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lista torneios do usuário"""
    tournaments = performance_service.get_user_tournaments(db, current_user.id, limit)
    
    return {
        "total": len(tournaments),
        "tournaments": [
            {
                "id": t.id,
                "tournament_id": t.tournament_id,
                "name": t.name or "Tournament",
                "buy_in": t.buy_in,
                "prize": t.prize,
                "position": t.position,
                "roi": t.roi,
                "is_itm": t.is_itm,
                "date_played": t.date_played.isoformat() if t.date_played else None,
                "platform": t.platform
            }
            for t in tournaments
        ]
    }

@router.post("/tournaments")
async def add_tournament(
    tournament_data: TournamentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Adiciona resultado de torneio manualmente"""
    from datetime import datetime
    
    tournament_dict = tournament_data.dict()
    tournament_dict['user_id'] = current_user.id
    
    # Converter data se fornecida
    if tournament_data.date_played:
        try:
            tournament_dict['date_played'] = datetime.fromisoformat(tournament_data.date_played)
        except:
            tournament_dict['date_played'] = datetime.now()
    else:
        tournament_dict['date_played'] = datetime.now()
    
    tournament = performance_service.add_tournament_result(db, current_user.id, tournament_dict)
    
    return {
        "message": "Tournament added successfully",
        "tournament": {
            "id": tournament.id,
            "tournament_id": tournament.tournament_id,
            "buy_in": tournament.buy_in,
            "prize": tournament.prize,
            "roi": tournament.roi,
            "is_itm": tournament.is_itm
        }
    }

@router.get("/roi-chart")
async def get_roi_chart(
    days_back: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém dados para gráfico de ROI"""
    chart_data = performance_service.get_roi_chart_data(db, current_user.id, days_back)
    
    return {
        "period_days": days_back,
        "data_points": len(chart_data),
        "chart_data": chart_data
    }

@router.get("/summary")
async def get_performance_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém resumo geral de performance"""
    
    # Stats para diferentes períodos
    stats_7d = performance_service.calculate_performance_stats(db, current_user.id, 7)
    stats_30d = performance_service.calculate_performance_stats(db, current_user.id, 30)
    stats_90d = performance_service.calculate_performance_stats(db, current_user.id, 90)
    
    return {
        "summary": {
            "last_7_days": stats_7d,
            "last_30_days": stats_30d,
            "last_90_days": stats_90d
        },
        "trends": {
            "roi_trend": _calculate_trend(stats_7d['roi_percentage'], stats_30d['roi_percentage']),
            "volume_trend": _calculate_trend(stats_7d['tournaments_played'], stats_30d['tournaments_played']),
            "itm_trend": _calculate_trend(stats_7d['itm_percentage'], stats_30d['itm_percentage'])
        }
    }

def _calculate_trend(recent: float, older: float) -> str:
    """Calcula tendência entre dois valores"""
    if recent == older == 0:
        return "stable"
    
    if older == 0:
        return "improving" if recent > 0 else "declining"
    
    change_percentage = ((recent - older) / abs(older)) * 100
    
    if change_percentage > 10:
        return "improving"
    elif change_percentage < -10:
        return "declining"
    else:
        return "stable"

