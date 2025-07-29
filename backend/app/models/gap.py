from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from app.models.database import Base

class Gap(Base):
    __tablename__ = "gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gap_type = Column(String(50), nullable=False)  # Ex: "preflop_aggression", "postflop_betting"
    description = Column(Text, nullable=False)
    frequency = Column(Integer, default=1)  # Quantas vezes foi identificado
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    first_identified = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    improvement_suggestion = Column(Text)
    
    # RELACIONAMENTO REMOVIDO TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Será reativado após correção dos relacionamentos
    # user = relationship("User", back_populates="gaps")

