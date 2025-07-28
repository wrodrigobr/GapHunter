from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.database import get_db
from app.models.user import User
from app.services.auth import get_current_active_user
from app.services.coach_service import CoachService, GapHunterVisionService

router = APIRouter()
coach_service = CoachService()
vision_service = GapHunterVisionService()

# Schemas
class CoachProfileCreate(BaseModel):
    bio: str = ""
    specialties: List[str] = []
    experience_years: int = 0
    hourly_rate: float = 0.0
    max_students: int = 10

class CoachingSessionCreate(BaseModel):
    student_id: int
    title: str
    description: str = ""
    session_date: str
    duration_minutes: int = 60

class StudentNoteCreate(BaseModel):
    student_id: int
    title: str
    content: str
    category: str = "general"
    priority: str = "medium"

class VisionSettingsUpdate(BaseModel):
    is_profile_public: bool = False
    allow_gap_analysis: bool = False
    show_performance_stats: bool = False
    show_recent_hands: bool = False
    hide_real_name: bool = True
    hide_earnings: bool = True

class PlayerAnalysisCreate(BaseModel):
    target_id: int
    analysis_type: str = "gap_analysis"
    notes: str = ""
    identified_gaps: List[str] = []
    strengths: str = ""
    recommendations: str = ""
    hands_analyzed: int = 0
    confidence_score: float = 0.0

# Endpoints de Coaching
@router.post("/coach/profile")
async def create_coach_profile(
    profile_data: CoachProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cria perfil de coach"""
    coach = coach_service.create_coach_profile(
        db, 
        current_user.id, 
        profile_data.dict()
    )
    
    return {
        "message": "Coach profile created successfully",
        "coach_id": coach.id
    }

@router.get("/coaches")
async def get_available_coaches(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Lista coaches disponíveis"""
    coaches = coach_service.get_available_coaches(db, limit)
    
    return {
        "total": len(coaches),
        "coaches": coaches
    }

@router.post("/coach/students/{student_id}")
async def add_student(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Adiciona aluno ao coach atual"""
    from app.models.coach import Coach
    
    coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach profile not found")
    
    success = coach_service.add_student_to_coach(db, coach.id, student_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not add student")
    
    return {"message": "Student added successfully"}

@router.get("/coach/students")
async def get_my_students(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lista alunos do coach atual"""
    students = coach_service.get_coach_students(db, current_user.id)
    
    return {
        "total": len(students),
        "students": students
    }

@router.get("/coach/students/{student_id}/progress")
async def get_student_progress(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém progresso detalhado de um aluno"""
    progress = coach_service.get_student_progress(db, current_user.id, student_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail="Student not found or not authorized")
    
    return progress

@router.post("/coach/sessions")
async def create_coaching_session(
    session_data: CoachingSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cria nova sessão de coaching"""
    from app.models.coach import Coach
    
    coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach profile not found")
    
    session_dict = session_data.dict()
    session_dict['coach_id'] = coach.id
    
    session = coach_service.create_coaching_session(db, session_dict)
    
    return {
        "message": "Coaching session created successfully",
        "session_id": session.id
    }

@router.post("/coach/notes")
async def add_student_note(
    note_data: StudentNoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Adiciona nota sobre um aluno"""
    from app.models.coach import Coach
    
    coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach profile not found")
    
    note_dict = note_data.dict()
    note_dict['coach_id'] = coach.id
    
    note = coach_service.add_student_note(db, note_dict)
    
    return {
        "message": "Note added successfully",
        "note_id": note.id
    }

# Endpoints GapHunter Vision
@router.put("/vision/settings")
async def update_vision_settings(
    settings: VisionSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualiza configurações do GapHunter Vision"""
    vision_settings = vision_service.setup_vision_settings(
        db, 
        current_user.id, 
        settings.dict()
    )
    
    return {
        "message": "Vision settings updated successfully",
        "settings": {
            "is_profile_public": vision_settings.is_profile_public,
            "allow_gap_analysis": vision_settings.allow_gap_analysis,
            "show_performance_stats": vision_settings.show_performance_stats,
            "show_recent_hands": vision_settings.show_recent_hands
        }
    }

@router.get("/vision/settings")
async def get_vision_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém configurações atuais do Vision"""
    from app.models.coach import GapHunterVision
    
    settings = db.query(GapHunterVision).filter(
        GapHunterVision.user_id == current_user.id
    ).first()
    
    if not settings:
        # Criar configurações padrão
        settings = vision_service.setup_vision_settings(db, current_user.id, {})
    
    return {
        "is_profile_public": settings.is_profile_public,
        "allow_gap_analysis": settings.allow_gap_analysis,
        "show_performance_stats": settings.show_performance_stats,
        "show_recent_hands": settings.show_recent_hands,
        "hide_real_name": settings.hide_real_name,
        "hide_earnings": settings.hide_earnings
    }

@router.get("/vision/players")
async def get_public_players(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista jogadores com perfil público"""
    players = vision_service.get_public_players(db, limit)
    
    return {
        "total": len(players),
        "players": players
    }

@router.post("/vision/analyze")
async def analyze_player(
    analysis_data: PlayerAnalysisCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cria análise de um jogador"""
    analysis = vision_service.analyze_player(
        db, 
        current_user.id, 
        analysis_data.target_id,
        analysis_data.dict()
    )
    
    if not analysis:
        raise HTTPException(
            status_code=403, 
            detail="Player analysis not allowed. Both players must have public profiles."
        )
    
    return {
        "message": "Player analysis created successfully",
        "analysis_id": analysis.id
    }

@router.get("/vision/analyses")
async def get_my_analyses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém análises feitas e recebidas pelo usuário"""
    analyses = vision_service.get_player_analyses(db, current_user.id)
    
    return analyses

