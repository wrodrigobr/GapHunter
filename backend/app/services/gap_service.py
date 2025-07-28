from sqlalchemy.orm import Session
from typing import List, Dict
import re
from datetime import datetime, timedelta

from app.models.hand import Hand
from app.models.gap import Gap
from app.models.user import User

class GapIdentificationService:
    def __init__(self):
        self.gap_patterns = {
            'preflop_aggression': {
                'keywords': ['fold', 'call', 'passive', 'tight'],
                'description': 'Falta de agressividade no pré-flop',
                'suggestion': 'Considere aumentar a frequência de raises em posições favoráveis'
            },
            'postflop_betting': {
                'keywords': ['check', 'call', 'passive betting'],
                'description': 'Jogo passivo no pós-flop',
                'suggestion': 'Trabalhe em estratégias de value betting e bluff'
            },
            'position_awareness': {
                'keywords': ['early position', 'out of position', 'position'],
                'description': 'Problemas com consciência posicional',
                'suggestion': 'Estude ranges por posição e ajuste sua estratégia'
            },
            'stack_management': {
                'keywords': ['stack', 'all-in', 'short stack', 'deep stack'],
                'description': 'Gestão inadequada de stack',
                'suggestion': 'Pratique conceitos de ICM e gestão de bankroll'
            },
            'bluff_frequency': {
                'keywords': ['bluff', 'semi-bluff', 'missed draw'],
                'description': 'Frequência de bluff inadequada',
                'suggestion': 'Balance sua frequência de bluff baseado em pot odds'
            }
        }

    def analyze_user_gaps(self, db: Session, user_id: int, days_back: int = 30) -> List[Dict]:
        """Analisa gaps recorrentes do usuário baseado nas últimas mãos"""
        
        # Buscar mãos recentes do usuário
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        recent_hands = db.query(Hand).filter(
            Hand.user_id == user_id,
            Hand.created_at >= cutoff_date
        ).all()

        if len(recent_hands) < 5:  # Mínimo de mãos para análise
            return []

        # Analisar padrões nas análises da IA
        identified_gaps = {}
        
        for hand in recent_hands:
            if hand.ai_analysis:
                gaps_found = self._extract_gaps_from_analysis(hand.ai_analysis)
                for gap_type, details in gaps_found.items():
                    if gap_type not in identified_gaps:
                        identified_gaps[gap_type] = {
                            'count': 0,
                            'details': details,
                            'hands': []
                        }
                    identified_gaps[gap_type]['count'] += 1
                    identified_gaps[gap_type]['hands'].append(hand.id)

        # Filtrar gaps significativos (aparecem em pelo menos 20% das mãos)
        min_frequency = max(1, len(recent_hands) * 0.2)
        significant_gaps = {
            gap_type: data for gap_type, data in identified_gaps.items()
            if data['count'] >= min_frequency
        }

        # Salvar ou atualizar gaps no banco
        self._update_user_gaps(db, user_id, significant_gaps)

        return self._format_gaps_response(significant_gaps)

    def _extract_gaps_from_analysis(self, analysis_text: str) -> Dict:
        """Extrai gaps da análise da IA usando padrões de texto"""
        gaps_found = {}
        analysis_lower = analysis_text.lower()

        for gap_type, pattern_data in self.gap_patterns.items():
            keyword_matches = sum(1 for keyword in pattern_data['keywords'] 
                                if keyword in analysis_lower)
            
            if keyword_matches >= 2:  # Pelo menos 2 keywords relacionadas
                gaps_found[gap_type] = {
                    'description': pattern_data['description'],
                    'suggestion': pattern_data['suggestion'],
                    'confidence': min(keyword_matches / len(pattern_data['keywords']), 1.0)
                }

        return gaps_found

    def _update_user_gaps(self, db: Session, user_id: int, gaps_data: Dict):
        """Atualiza gaps do usuário no banco de dados"""
        for gap_type, data in gaps_data.items():
            existing_gap = db.query(Gap).filter(
                Gap.user_id == user_id,
                Gap.gap_type == gap_type
            ).first()

            if existing_gap:
                # Atualizar gap existente
                existing_gap.frequency += data['count']
                existing_gap.last_seen = datetime.utcnow()
                existing_gap.severity = self._calculate_severity(existing_gap.frequency)
            else:
                # Criar novo gap
                new_gap = Gap(
                    user_id=user_id,
                    gap_type=gap_type,
                    description=data['details']['description'],
                    frequency=data['count'],
                    severity=self._calculate_severity(data['count']),
                    improvement_suggestion=data['details']['suggestion']
                )
                db.add(new_gap)

        db.commit()

    def _calculate_severity(self, frequency: int) -> str:
        """Calcula severidade baseada na frequência"""
        if frequency >= 10:
            return "critical"
        elif frequency >= 5:
            return "high"
        elif frequency >= 3:
            return "medium"
        else:
            return "low"

    def _format_gaps_response(self, gaps_data: Dict) -> List[Dict]:
        """Formata resposta dos gaps para o frontend"""
        formatted_gaps = []
        
        for gap_type, data in gaps_data.items():
            formatted_gaps.append({
                'type': gap_type,
                'description': data['details']['description'],
                'frequency': data['count'],
                'severity': self._calculate_severity(data['count']),
                'suggestion': data['details']['suggestion'],
                'confidence': data['details']['confidence']
            })

        # Ordenar por severidade e frequência
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        formatted_gaps.sort(
            key=lambda x: (severity_order[x['severity']], x['frequency']), 
            reverse=True
        )

        return formatted_gaps

    def get_user_gaps_summary(self, db: Session, user_id: int) -> Dict:
        """Obtém resumo dos gaps do usuário"""
        gaps = db.query(Gap).filter(Gap.user_id == user_id).all()
        
        if not gaps:
            return {
                'total_gaps': 0,
                'critical_gaps': 0,
                'most_common_gap': None,
                'improvement_areas': []
            }

        critical_gaps = [g for g in gaps if g.severity == 'critical']
        most_common = max(gaps, key=lambda g: g.frequency)

        return {
            'total_gaps': len(gaps),
            'critical_gaps': len(critical_gaps),
            'most_common_gap': {
                'type': most_common.gap_type,
                'description': most_common.description,
                'frequency': most_common.frequency
            },
            'improvement_areas': [
                {
                    'type': gap.gap_type,
                    'description': gap.description,
                    'suggestion': gap.improvement_suggestion,
                    'severity': gap.severity
                }
                for gap in sorted(gaps, key=lambda g: g.frequency, reverse=True)[:5]
            ]
        }

