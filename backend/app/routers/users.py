from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.models.schemas import User as UserSchema
from app.services.auth import get_current_active_user

router = APIRouter()

@router.get("/profile", response_model=UserSchema)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter perfil do usuário atual"""
    return current_user

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas do usuário"""
    from app.models.hand import Hand
    
    total_hands = db.query(Hand).filter(Hand.user_id == current_user.id).count()
    
    return {
        "total_hands": total_hands,
        "username": current_user.username,
        "member_since": current_user.created_at
    }

