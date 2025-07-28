from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.user import User
from app.services.auth import get_current_active_user
from app.services.gap_service import GapIdentificationService

router = APIRouter()
gap_service = GapIdentificationService()

@router.get("/analyze")
async def analyze_gaps(
    days_back: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analisa gaps recorrentes do usuário"""
    gaps = gap_service.analyze_user_gaps(db, current_user.id, days_back)
    return {
        "gaps_identified": len(gaps),
        "analysis_period_days": days_back,
        "gaps": gaps
    }

@router.get("/summary")
async def get_gaps_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém resumo dos gaps do usuário"""
    summary = gap_service.get_user_gaps_summary(db, current_user.id)
    return summary

@router.get("/my-gaps")
async def get_my_gaps(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lista todos os gaps identificados do usuário"""
    from app.models.gap import Gap
    
    gaps = db.query(Gap).filter(Gap.user_id == current_user.id).order_by(
        Gap.severity.desc(), Gap.frequency.desc()
    ).all()
    
    return {
        "total": len(gaps),
        "gaps": [
            {
                "id": gap.id,
                "type": gap.gap_type,
                "description": gap.description,
                "frequency": gap.frequency,
                "severity": gap.severity,
                "first_identified": gap.first_identified,
                "last_seen": gap.last_seen,
                "suggestion": gap.improvement_suggestion
            }
            for gap in gaps
        ]
    }

