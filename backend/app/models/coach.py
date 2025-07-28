from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base

# Tabela de associação para relacionamento many-to-many entre coaches e alunos
coach_student_association = Table(
    'coach_students',
    Base.metadata,
    Column('coach_id', Integer, ForeignKey('coaches.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('is_active', Boolean, default=True)
)

class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Informações do coach
    bio = Column(Text)
    specialties = Column(String(500))  # JSON string com especialidades
    experience_years = Column(Integer)
    hourly_rate = Column(Float)
    
    # Configurações
    is_accepting_students = Column(Boolean, default=True)
    max_students = Column(Integer, default=10)
    
    # Estatísticas
    total_students = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="coach_profile")
    students = relationship("User", secondary=coach_student_association, back_populates="coaches")
    coaching_sessions = relationship("CoachingSession", back_populates="coach")
    student_notes = relationship("StudentNote", back_populates="coach")

class CoachingSession(Base):
    __tablename__ = "coaching_sessions"

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dados da sessão
    title = Column(String(200), nullable=False)
    description = Column(Text)
    session_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled
    
    # Análise da sessão
    hands_reviewed = Column(Integer, default=0)
    gaps_identified = Column(Text)  # JSON string
    homework_assigned = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    coach = relationship("Coach", back_populates="coaching_sessions")
    student = relationship("User", back_populates="coaching_sessions")

class StudentNote(Base):
    __tablename__ = "student_notes"

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Conteúdo da nota
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # "gap", "improvement", "homework", "general"
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Status
    is_resolved = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    coach = relationship("Coach", back_populates="student_notes")
    student = relationship("User", back_populates="coach_notes")

class GapHunterVision(Base):
    __tablename__ = "gaphunter_vision"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Configurações de visibilidade
    is_profile_public = Column(Boolean, default=False)
    allow_gap_analysis = Column(Boolean, default=False)
    show_performance_stats = Column(Boolean, default=False)
    show_recent_hands = Column(Boolean, default=False)
    
    # Configurações de privacidade
    hide_real_name = Column(Boolean, default=True)
    hide_earnings = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento
    user = relationship("User", back_populates="vision_settings")

class PlayerAnalysis(Base):
    __tablename__ = "player_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analyzer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Quem está analisando
    target_id = Column(Integer, ForeignKey("users.id"), nullable=False)    # Quem está sendo analisado
    
    # Dados da análise
    analysis_type = Column(String(50), default="gap_analysis")  # gap_analysis, performance_review
    notes = Column(Text)
    identified_gaps = Column(Text)  # JSON string
    strengths = Column(Text)
    recommendations = Column(Text)
    
    # Metadados
    hands_analyzed = Column(Integer, default=0)
    confidence_score = Column(Float)  # 0-100
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    analyzer = relationship("User", foreign_keys=[analyzer_id], back_populates="analyses_made")
    target = relationship("User", foreign_keys=[target_id], back_populates="analyses_received")

