from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tournament_id = Column(String(50), nullable=False)  # ID do torneio no site
    name = Column(String(200))
    buy_in = Column(Float, nullable=False)
    prize_pool = Column(Float)
    players_count = Column(Integer)
    position = Column(Integer)  # Posição final
    prize = Column(Float, default=0.0)  # Premiação recebida
    date_played = Column(DateTime(timezone=True), nullable=False)
    platform = Column(String(50), default="PokerStars")  # PokerStars, 888poker, etc.
    
    # Estatísticas calculadas
    roi = Column(Float)  # Return on Investment
    is_itm = Column(Boolean, default=False)  # In The Money
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="tournaments")
    hands = relationship("Hand", back_populates="tournament")

class PerformanceStats(Base):
    __tablename__ = "performance_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Período das estatísticas
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Estatísticas financeiras
    total_buy_ins = Column(Float, default=0.0)
    total_prizes = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)
    
    # Estatísticas de volume
    tournaments_played = Column(Integer, default=0)
    itm_count = Column(Integer, default=0)  # In The Money count
    itm_percentage = Column(Float, default=0.0)
    
    # Estatísticas de posicionamento
    avg_finish_position = Column(Float)
    best_finish = Column(Integer)
    worst_finish = Column(Integer)
    
    # Estatísticas por buy-in
    avg_buy_in = Column(Float, default=0.0)
    biggest_win = Column(Float, default=0.0)
    biggest_loss = Column(Float, default=0.0)
    
    # Tendências
    roi_trend = Column(String(20))  # 'improving', 'declining', 'stable'
    volume_trend = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento
    user = relationship("User", back_populates="performance_stats")

