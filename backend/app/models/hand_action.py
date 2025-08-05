from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base

class HandAction(Base):
    __tablename__ = "hand_actions"

    id = Column(Integer, primary_key=True, index=True)
    hand_id = Column(Integer, ForeignKey("hands.id"), nullable=False)
    street = Column(String(20), nullable=False)  # preflop, flop, turn, river
    player_name = Column(String(50), nullable=False)
    action_type = Column(String(20), nullable=False)  # fold, check, call, bet, raise, all-in
    amount = Column(Float, default=0.0)
    total_bet = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action_order = Column(Integer, nullable=False)  # Ordem da ação na street
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento com a tabela hands
    hand = relationship("Hand", back_populates="actions")

    def __repr__(self):
        return f"<HandAction(id={self.id}, hand_id={self.hand_id}, street='{self.street}', player='{self.player_name}', action='{self.action_type}')>"

    @property
    def formatted_amount(self):
        """Retorna o valor formatado como string"""
        if self.amount == 0:
            return "0"
        return f"${self.amount:.2f}"

    @property
    def formatted_total_bet(self):
        """Retorna o total da aposta formatado como string"""
        if self.total_bet == 0:
            return "0"
        return f"${self.total_bet:.2f}"

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'hand_id': self.hand_id,
            'street': self.street,
            'player_name': self.player_name,
            'action_type': self.action_type,
            'amount': self.amount,
            'total_bet': self.total_bet,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action_order': self.action_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 