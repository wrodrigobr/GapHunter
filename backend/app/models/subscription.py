from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, Enum
from sqlalchemy.sql import func
from app.models.database import Base
import enum

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    COACH = "coach"
    PREMIUM = "premium"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Plano e status
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    
    # Datas
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    next_billing_date = Column(DateTime(timezone=True))
    
    # Valores
    monthly_price = Column(Float, default=0.0)
    yearly_price = Column(Float, default=0.0)
    is_yearly = Column(Boolean, default=False)
    
    # Pagamento
    payment_method = Column(String(50))  # stripe, paypal, etc.
    external_subscription_id = Column(String(100))  # ID no provedor de pagamento
    
    # Afiliado
    referred_by = Column(Integer, ForeignKey("affiliates.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # RELACIONAMENTOS REMOVIDOS TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Serão reativados após correção dos relacionamentos
    # user = relationship("User", back_populates="subscription")
    # affiliate = relationship("Affiliate", back_populates="referrals")

class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informações do afiliado
    affiliate_code = Column(String(20), unique=True, nullable=False)
    is_influencer = Column(Boolean, default=False)
    
    # Comissões
    commission_rate = Column(Float, default=0.30)  # 30% padrão
    total_earnings = Column(Float, default=0.0)
    pending_earnings = Column(Float, default=0.0)
    paid_earnings = Column(Float, default=0.0)
    
    # Estatísticas
    total_referrals = Column(Integer, default=0)
    active_referrals = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # RELACIONAMENTOS REMOVIDOS TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Serão reativados após correção dos relacionamentos
    # user = relationship("User", back_populates="affiliate_profile")
    # referrals = relationship("Subscription", back_populates="affiliate")
    # commissions = relationship("Commission", back_populates="affiliate")

class Commission(Base):
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Valores
    amount = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    
    # Status
    status = Column(String(20), default="pending")  # pending, paid, cancelled
    
    # Datas
    earned_date = Column(DateTime(timezone=True), server_default=func.now())
    paid_date = Column(DateTime(timezone=True))
    
    # RELACIONAMENTOS REMOVIDOS TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Serão reativados após correção dos relacionamentos
    # affiliate = relationship("Affiliate", back_populates="commissions")
    # subscription = relationship("Subscription")

class FeatureAccess(Base):
    __tablename__ = "feature_access"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Módulos disponíveis
    gaphunter_core = Column(Boolean, default=True)
    performance_tracker = Column(Boolean, default=False)
    coaching_module = Column(Boolean, default=False)
    gaphunter_vision = Column(Boolean, default=False)
    ai_advanced = Column(Boolean, default=False)
    club_access = Column(Boolean, default=False)
    
    # Limites
    max_hands_per_month = Column(Integer, default=10)
    max_gap_analyses = Column(Integer, default=5)
    max_coach_students = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # RELACIONAMENTO REMOVIDO TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Será reativado após correção dos relacionamentos
    # user = relationship("User", back_populates="feature_access")

class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Detalhes do pagamento
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50))
    
    # Status
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    
    # IDs externos
    external_payment_id = Column(String(100))
    external_invoice_id = Column(String(100))
    
    # Datas
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    processed_date = Column(DateTime(timezone=True))
    
    # RELACIONAMENTOS REMOVIDOS TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Serão reativados após correção dos relacionamentos
    # user = relationship("User")
    # subscription = relationship("Subscription")

class ClubMember(Base):
    __tablename__ = "club_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status no clube
    member_level = Column(String(20), default="bronze")  # bronze, silver, gold, diamond
    points = Column(Integer, default=0)
    
    # Benefícios
    discount_percentage = Column(Float, default=0.0)
    priority_support = Column(Boolean, default=False)
    exclusive_content = Column(Boolean, default=False)
    
    # Atividade
    last_activity = Column(DateTime(timezone=True))
    total_referrals = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # RELACIONAMENTO REMOVIDO TEMPORARIAMENTE PARA CORRIGIR ERRO 500
    # Será reativado após correção dos relacionamentos
    # user = relationship("User", back_populates="club_membership")

