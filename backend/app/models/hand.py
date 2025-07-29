from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base

class Hand(Base):
    __tablename__ = "hands"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tournament_id = Column(String(50), nullable=True)  # ID do torneio como string
    hand_id = Column(String(50), nullable=False)  # ID da mão no arquivo
    
    # Dados do PokerStars
    pokerstars_tournament_id = Column(String(50))
    table_name = Column(String(100))
    date_played = Column(DateTime)
    hero_name = Column(String(50))
    hero_position = Column(String(10))
    hero_cards = Column(String(10))
    hero_action = Column(String(20))
    pot_size = Column(Float)
    bet_amount = Column(Float)
    board_cards = Column(String(20))
    raw_hand = Column(Text)  # Texto original da mão
    ai_analysis = Column(Text)  # Análise da IA
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="hands")

