from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import secrets
import string

from app.models.subscription import (
    Subscription, Affiliate, Commission, FeatureAccess, 
    PaymentHistory, ClubMember, SubscriptionPlan, SubscriptionStatus
)
from app.models.user import User

class SubscriptionService:
    def __init__(self):
        self.plan_features = {
            SubscriptionPlan.FREE: {
                'max_hands_per_month': 10,
                'max_gap_analyses': 5,
                'performance_tracker': False,
                'coaching_module': False,
                'gaphunter_vision': False,
                'ai_advanced': False,
                'club_access': False,
                'max_coach_students': 0,
                'price_monthly': 0.0,
                'price_yearly': 0.0
            },
            SubscriptionPlan.BASIC: {
                'max_hands_per_month': 100,
                'max_gap_analyses': 50,
                'performance_tracker': True,
                'coaching_module': False,
                'gaphunter_vision': False,
                'ai_advanced': False,
                'club_access': False,
                'max_coach_students': 0,
                'price_monthly': 9.99,
                'price_yearly': 99.99
            },
            SubscriptionPlan.PRO: {
                'max_hands_per_month': 500,
                'max_gap_analyses': 200,
                'performance_tracker': True,
                'coaching_module': True,
                'gaphunter_vision': True,
                'ai_advanced': True,
                'club_access': True,
                'max_coach_students': 5,
                'price_monthly': 29.99,
                'price_yearly': 299.99
            },
            SubscriptionPlan.COACH: {
                'max_hands_per_month': 1000,
                'max_gap_analyses': 500,
                'performance_tracker': True,
                'coaching_module': True,
                'gaphunter_vision': True,
                'ai_advanced': True,
                'club_access': True,
                'max_coach_students': 20,
                'price_monthly': 49.99,
                'price_yearly': 499.99
            },
            SubscriptionPlan.PREMIUM: {
                'max_hands_per_month': -1,  # Ilimitado
                'max_gap_analyses': -1,
                'performance_tracker': True,
                'coaching_module': True,
                'gaphunter_vision': True,
                'ai_advanced': True,
                'club_access': True,
                'max_coach_students': 50,
                'price_monthly': 99.99,
                'price_yearly': 999.99
            }
        }

    def create_subscription(self, db: Session, user_id: int, plan: SubscriptionPlan, 
                          is_yearly: bool = False, affiliate_code: str = None) -> Subscription:
        """Cria nova assinatura para usuário"""
        
        # Verificar se já existe assinatura ativa
        existing = db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        ).first()
        
        if existing:
            # Cancelar assinatura existente
            existing.status = SubscriptionStatus.CANCELLED
        
        # Buscar afiliado se código fornecido
        affiliate = None
        if affiliate_code:
            affiliate = db.query(Affiliate).filter(
                Affiliate.affiliate_code == affiliate_code
            ).first()
        
        # Calcular preços
        plan_info = self.plan_features[plan]
        monthly_price = plan_info['price_monthly']
        yearly_price = plan_info['price_yearly']
        
        # Criar assinatura
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            monthly_price=monthly_price,
            yearly_price=yearly_price,
            is_yearly=is_yearly,
            end_date=datetime.utcnow() + timedelta(days=365 if is_yearly else 30),
            next_billing_date=datetime.utcnow() + timedelta(days=365 if is_yearly else 30),
            referred_by=affiliate.id if affiliate else None
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # Atualizar acesso às funcionalidades
        self.update_feature_access(db, user_id, plan)
        
        # Processar comissão de afiliado
        if affiliate:
            self.process_affiliate_commission(db, affiliate.id, subscription.id)
        
        return subscription

    def update_feature_access(self, db: Session, user_id: int, plan: SubscriptionPlan):
        """Atualiza acesso às funcionalidades baseado no plano"""
        
        plan_info = self.plan_features[plan]
        
        # Buscar ou criar FeatureAccess
        feature_access = db.query(FeatureAccess).filter(
            FeatureAccess.user_id == user_id
        ).first()
        
        if not feature_access:
            feature_access = FeatureAccess(user_id=user_id)
            db.add(feature_access)
        
        # Atualizar funcionalidades
        feature_access.performance_tracker = plan_info['performance_tracker']
        feature_access.coaching_module = plan_info['coaching_module']
        feature_access.gaphunter_vision = plan_info['gaphunter_vision']
        feature_access.ai_advanced = plan_info['ai_advanced']
        feature_access.club_access = plan_info['club_access']
        feature_access.max_hands_per_month = plan_info['max_hands_per_month']
        feature_access.max_gap_analyses = plan_info['max_gap_analyses']
        feature_access.max_coach_students = plan_info['max_coach_students']
        
        db.commit()

    def get_user_subscription(self, db: Session, user_id: int) -> Optional[Dict]:
        """Obtém assinatura ativa do usuário"""
        
        subscription = db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        ).first()
        
        if not subscription:
            return None
        
        return {
            'id': subscription.id,
            'plan': subscription.plan.value,
            'status': subscription.status.value,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            'next_billing_date': subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            'monthly_price': subscription.monthly_price,
            'yearly_price': subscription.yearly_price,
            'is_yearly': subscription.is_yearly,
            'payment_method': subscription.payment_method
        }

    def check_feature_access(self, db: Session, user_id: int, feature: str) -> bool:
        """Verifica se usuário tem acesso a uma funcionalidade"""
        
        feature_access = db.query(FeatureAccess).filter(
            FeatureAccess.user_id == user_id
        ).first()
        
        if not feature_access:
            # Criar acesso padrão (FREE)
            self.update_feature_access(db, user_id, SubscriptionPlan.FREE)
            feature_access = db.query(FeatureAccess).filter(
                FeatureAccess.user_id == user_id
            ).first()
        
        return getattr(feature_access, feature, False)

class AffiliateService:
    def __init__(self):
        pass

    def generate_affiliate_code(self) -> str:
        """Gera código único de afiliado"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    def create_affiliate(self, db: Session, user_id: int, is_influencer: bool = False) -> Affiliate:
        """Cria perfil de afiliado"""
        
        # Verificar se já existe
        existing = db.query(Affiliate).filter(Affiliate.user_id == user_id).first()
        if existing:
            return existing
        
        # Gerar código único
        affiliate_code = self.generate_affiliate_code()
        while db.query(Affiliate).filter(Affiliate.affiliate_code == affiliate_code).first():
            affiliate_code = self.generate_affiliate_code()
        
        # Definir taxa de comissão
        commission_rate = 0.50 if is_influencer else 0.30  # 50% para influenciadores, 30% padrão
        
        affiliate = Affiliate(
            user_id=user_id,
            affiliate_code=affiliate_code,
            is_influencer=is_influencer,
            commission_rate=commission_rate
        )
        
        db.add(affiliate)
        db.commit()
        db.refresh(affiliate)
        
        return affiliate

    def process_commission(self, db: Session, affiliate_id: int, subscription_id: int):
        """Processa comissão de afiliado"""
        
        affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        
        if not affiliate or not subscription:
            return
        
        # Calcular comissão
        amount = subscription.yearly_price if subscription.is_yearly else subscription.monthly_price
        commission_amount = amount * affiliate.commission_rate
        
        # Criar registro de comissão
        commission = Commission(
            affiliate_id=affiliate_id,
            subscription_id=subscription_id,
            amount=commission_amount,
            percentage=affiliate.commission_rate * 100
        )
        
        db.add(commission)
        
        # Atualizar estatísticas do afiliado
        affiliate.total_referrals += 1
        affiliate.active_referrals += 1
        affiliate.pending_earnings += commission_amount
        affiliate.total_earnings += commission_amount
        
        # Recalcular taxa de conversão
        total_clicks = affiliate.total_referrals * 10  # Estimativa
        affiliate.conversion_rate = (affiliate.total_referrals / total_clicks) * 100 if total_clicks > 0 else 0
        
        db.commit()

    def get_affiliate_stats(self, db: Session, user_id: int) -> Optional[Dict]:
        """Obtém estatísticas do afiliado"""
        
        affiliate = db.query(Affiliate).filter(Affiliate.user_id == user_id).first()
        if not affiliate:
            return None
        
        # Comissões recentes
        recent_commissions = db.query(Commission).filter(
            Commission.affiliate_id == affiliate.id
        ).order_by(desc(Commission.earned_date)).limit(10).all()
        
        return {
            'affiliate_code': affiliate.affiliate_code,
            'is_influencer': affiliate.is_influencer,
            'commission_rate': affiliate.commission_rate * 100,
            'total_earnings': affiliate.total_earnings,
            'pending_earnings': affiliate.pending_earnings,
            'paid_earnings': affiliate.paid_earnings,
            'total_referrals': affiliate.total_referrals,
            'active_referrals': affiliate.active_referrals,
            'conversion_rate': affiliate.conversion_rate,
            'recent_commissions': [
                {
                    'id': c.id,
                    'amount': c.amount,
                    'percentage': c.percentage,
                    'status': c.status,
                    'earned_date': c.earned_date.isoformat()
                }
                for c in recent_commissions
            ]
        }

class ClubService:
    def __init__(self):
        self.level_requirements = {
            'bronze': {'points': 0, 'discount': 0.0},
            'silver': {'points': 100, 'discount': 0.05},
            'gold': {'points': 500, 'discount': 0.10},
            'diamond': {'points': 1000, 'discount': 0.15}
        }

    def create_club_membership(self, db: Session, user_id: int) -> ClubMember:
        """Cria membership no clube"""
        
        existing = db.query(ClubMember).filter(ClubMember.user_id == user_id).first()
        if existing:
            return existing
        
        member = ClubMember(
            user_id=user_id,
            member_level='bronze',
            points=0
        )
        
        db.add(member)
        db.commit()
        db.refresh(member)
        
        return member

    def add_points(self, db: Session, user_id: int, points: int, reason: str = "activity"):
        """Adiciona pontos ao membro"""
        
        member = db.query(ClubMember).filter(ClubMember.user_id == user_id).first()
        if not member:
            member = self.create_club_membership(db, user_id)
        
        member.points += points
        member.last_activity = datetime.utcnow()
        
        # Verificar upgrade de nível
        new_level = self.calculate_level(member.points)
        if new_level != member.member_level:
            member.member_level = new_level
            member.discount_percentage = self.level_requirements[new_level]['discount']
            
            # Atualizar benefícios
            if new_level in ['gold', 'diamond']:
                member.priority_support = True
                member.exclusive_content = True
        
        db.commit()

    def calculate_level(self, points: int) -> str:
        """Calcula nível baseado nos pontos"""
        
        for level in ['diamond', 'gold', 'silver', 'bronze']:
            if points >= self.level_requirements[level]['points']:
                return level
        
        return 'bronze'

    def get_club_stats(self, db: Session, user_id: int) -> Optional[Dict]:
        """Obtém estatísticas do clube"""
        
        member = db.query(ClubMember).filter(ClubMember.user_id == user_id).first()
        if not member:
            return None
        
        # Próximo nível
        current_points = member.points
        next_level = None
        points_to_next = 0
        
        levels = ['bronze', 'silver', 'gold', 'diamond']
        current_index = levels.index(member.member_level)
        
        if current_index < len(levels) - 1:
            next_level = levels[current_index + 1]
            points_to_next = self.level_requirements[next_level]['points'] - current_points
        
        return {
            'member_level': member.member_level,
            'points': member.points,
            'discount_percentage': member.discount_percentage * 100,
            'priority_support': member.priority_support,
            'exclusive_content': member.exclusive_content,
            'total_referrals': member.total_referrals,
            'next_level': next_level,
            'points_to_next_level': points_to_next,
            'member_since': member.created_at.isoformat()
        }

