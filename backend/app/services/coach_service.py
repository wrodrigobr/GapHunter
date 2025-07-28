from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

from app.models.coach import Coach, CoachingSession, StudentNote, GapHunterVision, PlayerAnalysis
from app.models.user import User
from app.models.gap import Gap
from app.models.hand import Hand

class CoachService:
    def __init__(self):
        pass

    def create_coach_profile(self, db: Session, user_id: int, coach_data: Dict) -> Coach:
        """Cria perfil de coach para um usuário"""
        
        # Verificar se já existe perfil de coach
        existing = db.query(Coach).filter(Coach.user_id == user_id).first()
        if existing:
            return existing
        
        coach = Coach(
            user_id=user_id,
            bio=coach_data.get('bio', ''),
            specialties=json.dumps(coach_data.get('specialties', [])),
            experience_years=coach_data.get('experience_years', 0),
            hourly_rate=coach_data.get('hourly_rate', 0.0),
            max_students=coach_data.get('max_students', 10)
        )
        
        db.add(coach)
        db.commit()
        db.refresh(coach)
        
        return coach

    def get_available_coaches(self, db: Session, limit: int = 20) -> List[Dict]:
        """Lista coaches disponíveis para novos alunos"""
        
        coaches = db.query(Coach).filter(
            and_(
                Coach.is_accepting_students == True,
                Coach.total_students < Coach.max_students
            )
        ).order_by(desc(Coach.rating)).limit(limit).all()
        
        result = []
        for coach in coaches:
            user = db.query(User).filter(User.id == coach.user_id).first()
            result.append({
                'id': coach.id,
                'username': user.username if user else 'Unknown',
                'bio': coach.bio,
                'specialties': json.loads(coach.specialties) if coach.specialties else [],
                'experience_years': coach.experience_years,
                'hourly_rate': coach.hourly_rate,
                'rating': coach.rating,
                'total_reviews': coach.total_reviews,
                'available_slots': coach.max_students - coach.total_students
            })
        
        return result

    def add_student_to_coach(self, db: Session, coach_id: int, student_id: int) -> bool:
        """Adiciona aluno a um coach"""
        
        coach = db.query(Coach).filter(Coach.id == coach_id).first()
        student = db.query(User).filter(User.id == student_id).first()
        
        if not coach or not student:
            return False
        
        if coach.total_students >= coach.max_students:
            return False
        
        # Verificar se já existe relacionamento
        if student in coach.students:
            return True
        
        coach.students.append(student)
        coach.total_students += 1
        
        db.commit()
        return True

    def get_coach_students(self, db: Session, coach_user_id: int) -> List[Dict]:
        """Obtém lista de alunos de um coach"""
        
        coach = db.query(Coach).filter(Coach.user_id == coach_user_id).first()
        if not coach:
            return []
        
        students_data = []
        for student in coach.students:
            # Obter estatísticas do aluno
            recent_gaps = db.query(Gap).filter(
                Gap.user_id == student.id
            ).order_by(desc(Gap.last_seen)).limit(5).all()
            
            recent_hands = db.query(Hand).filter(
                Hand.user_id == student.id
            ).order_by(desc(Hand.created_at)).limit(10).count()
            
            students_data.append({
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'member_since': student.created_at.isoformat(),
                'recent_hands_count': recent_hands,
                'active_gaps': len([g for g in recent_gaps if g.severity in ['high', 'critical']]),
                'last_activity': max([g.last_seen for g in recent_gaps]) if recent_gaps else None
            })
        
        return students_data

    def create_coaching_session(self, db: Session, session_data: Dict) -> CoachingSession:
        """Cria nova sessão de coaching"""
        
        session = CoachingSession(
            coach_id=session_data['coach_id'],
            student_id=session_data['student_id'],
            title=session_data['title'],
            description=session_data.get('description', ''),
            session_date=datetime.fromisoformat(session_data['session_date']),
            duration_minutes=session_data.get('duration_minutes', 60)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session

    def add_student_note(self, db: Session, note_data: Dict) -> StudentNote:
        """Adiciona nota sobre um aluno"""
        
        note = StudentNote(
            coach_id=note_data['coach_id'],
            student_id=note_data['student_id'],
            title=note_data['title'],
            content=note_data['content'],
            category=note_data.get('category', 'general'),
            priority=note_data.get('priority', 'medium')
        )
        
        db.add(note)
        db.commit()
        db.refresh(note)
        
        return note

    def get_student_progress(self, db: Session, coach_user_id: int, student_id: int) -> Dict:
        """Obtém progresso detalhado de um aluno"""
        
        coach = db.query(Coach).filter(Coach.user_id == coach_user_id).first()
        if not coach:
            return {}
        
        student = db.query(User).filter(User.id == student_id).first()
        if not student or student not in coach.students:
            return {}
        
        # Gaps do aluno
        gaps = db.query(Gap).filter(Gap.user_id == student_id).all()
        
        # Sessões de coaching
        sessions = db.query(CoachingSession).filter(
            and_(
                CoachingSession.coach_id == coach.id,
                CoachingSession.student_id == student_id
            )
        ).order_by(desc(CoachingSession.session_date)).all()
        
        # Notas do coach
        notes = db.query(StudentNote).filter(
            and_(
                StudentNote.coach_id == coach.id,
                StudentNote.student_id == student_id
            )
        ).order_by(desc(StudentNote.created_at)).all()
        
        # Mãos recentes
        recent_hands = db.query(Hand).filter(
            Hand.user_id == student_id
        ).order_by(desc(Hand.created_at)).limit(20).all()
        
        return {
            'student': {
                'id': student.id,
                'username': student.username,
                'member_since': student.created_at.isoformat()
            },
            'gaps_summary': {
                'total': len(gaps),
                'critical': len([g for g in gaps if g.severity == 'critical']),
                'high': len([g for g in gaps if g.severity == 'high']),
                'medium': len([g for g in gaps if g.severity == 'medium']),
                'low': len([g for g in gaps if g.severity == 'low'])
            },
            'gaps_detail': [
                {
                    'id': gap.id,
                    'type': gap.gap_type,
                    'description': gap.description,
                    'frequency': gap.frequency,
                    'severity': gap.severity,
                    'last_seen': gap.last_seen.isoformat() if gap.last_seen else None,
                    'suggestion': gap.improvement_suggestion
                }
                for gap in gaps
            ],
            'coaching_sessions': [
                {
                    'id': session.id,
                    'title': session.title,
                    'date': session.session_date.isoformat(),
                    'duration': session.duration_minutes,
                    'status': session.status,
                    'hands_reviewed': session.hands_reviewed,
                    'notes': session.notes
                }
                for session in sessions
            ],
            'coach_notes': [
                {
                    'id': note.id,
                    'title': note.title,
                    'content': note.content,
                    'category': note.category,
                    'priority': note.priority,
                    'is_resolved': note.is_resolved,
                    'created_at': note.created_at.isoformat()
                }
                for note in notes
            ],
            'recent_activity': {
                'hands_count': len(recent_hands),
                'last_hand_date': recent_hands[0].created_at.isoformat() if recent_hands else None
            }
        }

class GapHunterVisionService:
    def __init__(self):
        pass

    def setup_vision_settings(self, db: Session, user_id: int, settings: Dict) -> GapHunterVision:
        """Configura settings do GapHunter Vision para um usuário"""
        
        existing = db.query(GapHunterVision).filter(GapHunterVision.user_id == user_id).first()
        
        if existing:
            # Atualizar existente
            for key, value in settings.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
        else:
            # Criar novo
            existing = GapHunterVision(
                user_id=user_id,
                **settings
            )
            db.add(existing)
        
        db.commit()
        db.refresh(existing)
        
        return existing

    def get_public_players(self, db: Session, limit: int = 50) -> List[Dict]:
        """Lista jogadores com perfil público"""
        
        public_settings = db.query(GapHunterVision).filter(
            GapHunterVision.is_profile_public == True
        ).limit(limit).all()
        
        result = []
        for setting in public_settings:
            user = db.query(User).filter(User.id == setting.user_id).first()
            if not user:
                continue
            
            # Estatísticas básicas se permitidas
            stats = {}
            if setting.show_performance_stats:
                from app.services.performance_service import PerformanceAnalysisService
                perf_service = PerformanceAnalysisService()
                stats = perf_service.calculate_performance_stats(db, user.id, 30)
            
            # Gaps se permitidos
            gaps_summary = {}
            if setting.allow_gap_analysis:
                gaps = db.query(Gap).filter(Gap.user_id == user.id).all()
                gaps_summary = {
                    'total': len(gaps),
                    'critical': len([g for g in gaps if g.severity == 'critical']),
                    'most_common': gaps[0].gap_type if gaps else None
                }
            
            result.append({
                'id': user.id,
                'username': user.username if not setting.hide_real_name else f"Player_{user.id}",
                'member_since': user.created_at.isoformat(),
                'performance_stats': stats if setting.show_performance_stats else None,
                'gaps_summary': gaps_summary if setting.allow_gap_analysis else None,
                'privacy_settings': {
                    'show_performance': setting.show_performance_stats,
                    'allow_gap_analysis': setting.allow_gap_analysis,
                    'show_recent_hands': setting.show_recent_hands
                }
            })
        
        return result

    def analyze_player(self, db: Session, analyzer_id: int, target_id: int, analysis_data: Dict) -> Optional[PlayerAnalysis]:
        """Cria análise de um jogador por outro"""
        
        # Verificar se o target permite análise
        target_settings = db.query(GapHunterVision).filter(
            GapHunterVision.user_id == target_id
        ).first()
        
        if not target_settings or not target_settings.allow_gap_analysis:
            return None
        
        # Verificar se analyzer também tem perfil público (reciprocidade)
        analyzer_settings = db.query(GapHunterVision).filter(
            GapHunterVision.user_id == analyzer_id
        ).first()
        
        if not analyzer_settings or not analyzer_settings.is_profile_public:
            return None
        
        analysis = PlayerAnalysis(
            analyzer_id=analyzer_id,
            target_id=target_id,
            analysis_type=analysis_data.get('analysis_type', 'gap_analysis'),
            notes=analysis_data.get('notes', ''),
            identified_gaps=json.dumps(analysis_data.get('identified_gaps', [])),
            strengths=analysis_data.get('strengths', ''),
            recommendations=analysis_data.get('recommendations', ''),
            hands_analyzed=analysis_data.get('hands_analyzed', 0),
            confidence_score=analysis_data.get('confidence_score', 0.0)
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis

    def get_player_analyses(self, db: Session, user_id: int) -> Dict:
        """Obtém análises feitas e recebidas por um jogador"""
        
        analyses_made = db.query(PlayerAnalysis).filter(
            PlayerAnalysis.analyzer_id == user_id
        ).order_by(desc(PlayerAnalysis.created_at)).all()
        
        analyses_received = db.query(PlayerAnalysis).filter(
            PlayerAnalysis.target_id == user_id
        ).order_by(desc(PlayerAnalysis.created_at)).all()
        
        return {
            'analyses_made': [
                {
                    'id': analysis.id,
                    'target_username': db.query(User).filter(User.id == analysis.target_id).first().username,
                    'analysis_type': analysis.analysis_type,
                    'hands_analyzed': analysis.hands_analyzed,
                    'confidence_score': analysis.confidence_score,
                    'created_at': analysis.created_at.isoformat()
                }
                for analysis in analyses_made
            ],
            'analyses_received': [
                {
                    'id': analysis.id,
                    'analyzer_username': db.query(User).filter(User.id == analysis.analyzer_id).first().username,
                    'analysis_type': analysis.analysis_type,
                    'notes': analysis.notes,
                    'strengths': analysis.strengths,
                    'recommendations': analysis.recommendations,
                    'created_at': analysis.created_at.isoformat()
                }
                for analysis in analyses_received
            ]
        }

