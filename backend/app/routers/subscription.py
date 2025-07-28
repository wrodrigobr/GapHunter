from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.database import get_db
from app.models.user import User
from app.models.subscription import SubscriptionPlan
from app.services.auth import get_current_active_user
from app.services.subscription_service import SubscriptionService, AffiliateService, ClubService

router = APIRouter()
subscription_service = SubscriptionService()
affiliate_service = AffiliateService()
club_service = ClubService()

# Schemas
class SubscriptionCreate(BaseModel):
    plan: str
    is_yearly: bool = False
    affiliate_code: str = None

class AffiliateCreate(BaseModel):
    is_influencer: bool = False

# Endpoints de Assinatura
@router.get("/plans")
async def get_subscription_plans():
    """Lista planos de assinatura disponíveis"""
    
    plans = []
    for plan, features in subscription_service.plan_features.items():
        plans.append({
            'plan': plan.value,
            'name': plan.value.title(),
            'price_monthly': features['price_monthly'],
            'price_yearly': features['price_yearly'],
            'features': {
                'max_hands_per_month': features['max_hands_per_month'],
                'max_gap_analyses': features['max_gap_analyses'],
                'performance_tracker': features['performance_tracker'],
                'coaching_module': features['coaching_module'],
                'gaphunter_vision': features['gaphunter_vision'],
                'ai_advanced': features['ai_advanced'],
                'club_access': features['club_access'],
                'max_coach_students': features['max_coach_students']
            }
        })
    
    return {'plans': plans}

@router.get("/my-subscription")
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém assinatura atual do usuário"""
    
    subscription = subscription_service.get_user_subscription(db, current_user.id)
    
    if not subscription:
        return {
            'subscription': None,
            'plan': 'free',
            'message': 'No active subscription found'
        }
    
    return {'subscription': subscription}

@router.post("/subscribe")
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cria nova assinatura"""
    
    try:
        plan = SubscriptionPlan(subscription_data.plan)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    subscription = subscription_service.create_subscription(
        db,
        current_user.id,
        plan,
        subscription_data.is_yearly,
        subscription_data.affiliate_code
    )
    
    return {
        'message': 'Subscription created successfully',
        'subscription_id': subscription.id,
        'plan': subscription.plan.value,
        'end_date': subscription.end_date.isoformat()
    }

@router.get("/feature-access/{feature}")
async def check_feature_access(
    feature: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verifica acesso a uma funcionalidade específica"""
    
    has_access = subscription_service.check_feature_access(db, current_user.id, feature)
    
    return {
        'feature': feature,
        'has_access': has_access
    }

# Endpoints de Afiliados
@router.post("/affiliate/join")
async def join_affiliate_program(
    affiliate_data: AffiliateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ingressar no programa de afiliados"""
    
    affiliate = affiliate_service.create_affiliate(
        db,
        current_user.id,
        affiliate_data.is_influencer
    )
    
    return {
        'message': 'Successfully joined affiliate program',
        'affiliate_code': affiliate.affiliate_code,
        'commission_rate': affiliate.commission_rate * 100,
        'is_influencer': affiliate.is_influencer
    }

@router.get("/affiliate/stats")
async def get_affiliate_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas do afiliado"""
    
    stats = affiliate_service.get_affiliate_stats(db, current_user.id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Affiliate profile not found")
    
    return stats

@router.get("/affiliate/dashboard")
async def get_affiliate_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dashboard completo do afiliado"""
    
    stats = affiliate_service.get_affiliate_stats(db, current_user.id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Affiliate profile not found")
    
    # Calcular métricas adicionais
    monthly_earnings = stats['pending_earnings'] + stats['paid_earnings']
    avg_commission = monthly_earnings / stats['total_referrals'] if stats['total_referrals'] > 0 else 0
    
    return {
        'stats': stats,
        'metrics': {
            'monthly_earnings': monthly_earnings,
            'avg_commission_per_referral': avg_commission,
            'referral_link': f"https://gaphunter.com?ref={stats['affiliate_code']}",
            'performance_rating': 'Excellent' if stats['conversion_rate'] > 5 else 'Good' if stats['conversion_rate'] > 2 else 'Needs Improvement'
        }
    }

# Endpoints do Clube
@router.post("/club/join")
async def join_club(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ingressar no GapHunter Club"""
    
    # Verificar se tem acesso ao clube
    has_access = subscription_service.check_feature_access(db, current_user.id, 'club_access')
    
    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail="Club access requires Pro subscription or higher"
        )
    
    member = club_service.create_club_membership(db, current_user.id)
    
    return {
        'message': 'Successfully joined GapHunter Club',
        'member_level': member.member_level,
        'points': member.points
    }

@router.get("/club/stats")
async def get_club_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas do clube"""
    
    stats = club_service.get_club_stats(db, current_user.id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Club membership not found")
    
    return stats

@router.post("/club/add-points")
async def add_club_points(
    points: int = Query(..., ge=1, le=100),
    reason: str = Query("manual", max_length=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Adiciona pontos ao membro do clube (para demonstração)"""
    
    club_service.add_points(db, current_user.id, points, reason)
    
    stats = club_service.get_club_stats(db, current_user.id)
    
    return {
        'message': f'Added {points} points for {reason}',
        'new_stats': stats
    }

@router.get("/club/leaderboard")
async def get_club_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obtém ranking do clube"""
    
    from app.models.subscription import ClubMember
    
    top_members = db.query(ClubMember).order_by(
        ClubMember.points.desc()
    ).limit(limit).all()
    
    leaderboard = []
    for i, member in enumerate(top_members, 1):
        user = db.query(User).filter(User.id == member.user_id).first()
        leaderboard.append({
            'rank': i,
            'username': user.username if user else 'Unknown',
            'member_level': member.member_level,
            'points': member.points,
            'total_referrals': member.total_referrals
        })
    
    return {
        'leaderboard': leaderboard,
        'total_members': len(leaderboard)
    }

# Endpoints de Pagamento (simulado)
@router.post("/payment/simulate")
async def simulate_payment(
    subscription_id: int,
    amount: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Simula processamento de pagamento"""
    
    from app.models.subscription import PaymentHistory
    
    # Verificar se a assinatura pertence ao usuário
    subscription = db.query(Subscription).filter(
        and_(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Criar histórico de pagamento
    payment = PaymentHistory(
        user_id=current_user.id,
        subscription_id=subscription_id,
        amount=amount,
        payment_method="credit_card",
        status="completed",
        external_payment_id=f"sim_{datetime.utcnow().timestamp()}",
        processed_date=datetime.utcnow()
    )
    
    db.add(payment)
    db.commit()
    
    return {
        'message': 'Payment processed successfully',
        'payment_id': payment.id,
        'amount': amount,
        'status': 'completed'
    }

