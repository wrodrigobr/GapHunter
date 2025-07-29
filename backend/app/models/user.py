from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    nickname = Column(String(50), nullable=True)  # Apelido do jogador (temporariamente nullable)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Informações específicas de poker
    poker_experience = Column(String(20), nullable=True)  # "beginner", "intermediate", "advanced", "professional"
    preferred_games = Column(String(20), nullable=True)   # "cash", "tournaments", "both"
    main_stakes = Column(String(20), nullable=True)       # "micro", "low", "mid", "high"
    poker_goals = Column(String(20), nullable=True)       # "recreational", "profit", "professional"
    country = Column(String(50), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com mãos
    hands = relationship("Hand", back_populates="user")
    
    # Relacionamento com gaps
    gaps = relationship("Gap", back_populates="user")
    
    # Relacionamento com torneios
    tournaments = relationship("Tournament", back_populates="user")
    
    # Relacionamento com estatísticas de performance
    performance_stats = relationship("PerformanceStats", back_populates="user")
    
    # Relacionamentos de coaching
    coach_profile = relationship("Coach", back_populates="user", uselist=False)
    coaches = relationship("Coach", secondary="coach_students", back_populates="students")
    coaching_sessions = relationship("CoachingSession", back_populates="student")
    coach_notes = relationship("StudentNote", back_populates="student")
    
    # Relacionamentos GapHunter Vision
    vision_settings = relationship("GapHunterVision", back_populates="user", uselist=False)
    analyses_made = relationship("PlayerAnalysis", foreign_keys="PlayerAnalysis.analyzer_id", back_populates="analyzer")
    analyses_received = relationship("PlayerAnalysis", foreign_keys="PlayerAnalysis.target_id", back_populates="target")
    
    # Relacionamentos de assinatura e afiliados
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    affiliate_profile = relationship("Affiliate", back_populates="user", uselist=False)
    feature_access = relationship("FeatureAccess", back_populates="user", uselist=False)
    club_membership = relationship("ClubMember", back_populates="user", uselist=False)

