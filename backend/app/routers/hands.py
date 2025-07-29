from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime
import os

from app.models.database import get_db
from app.models.user import User
from app.models.hand import Hand
from app.models.tournament import Tournament
from app.models.schemas import Hand as HandSchema, UploadResponse
from app.services.auth import get_current_active_user
from app.utils.poker_parser import PokerStarsParser
from app.utils.advanced_poker_parser import parse_hand_for_table_replay
from app.services.ai_service import AIAnalysisService

router = APIRouter()
parser = PokerStarsParser()
ai_service = AIAnalysisService()

def get_or_create_tournament(db: Session, user_id: int, tournament_data: dict) -> Optional[Tournament]:
    """Busca ou cria um torneio na tabela tournaments"""
    
    pokerstars_tournament_id = tournament_data.get('tournament_id')
    if not pokerstars_tournament_id:
        return None
    
    # Buscar torneio existente
    existing_tournament = db.query(Tournament).filter(
        Tournament.user_id == user_id,
        Tournament.tournament_id == pokerstars_tournament_id
    ).first()
    
    if existing_tournament:
        return existing_tournament
    
    # Criar novo torneio
    try:
        new_tournament = Tournament(
            user_id=user_id,
            tournament_id=pokerstars_tournament_id,
            name=f"Torneio {pokerstars_tournament_id}",
            buy_in=0.0,  # Será extraído posteriormente se disponível
            date_played=tournament_data.get('date_played') or datetime.now(),
            platform="PokerStars"
        )
        
        db.add(new_tournament)
        db.flush()  # Para obter o ID sem fazer commit
        
        print(f"✅ Torneio {pokerstars_tournament_id} criado com ID {new_tournament.id}")
        return new_tournament
        
    except Exception as e:
        print(f"❌ Erro ao criar torneio {pokerstars_tournament_id}: {e}")
        return None

@router.post("/upload", response_model=UploadResponse)
async def upload_hand_history(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload de arquivo de hand history"""
    
    # Verificar se é arquivo .txt
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Apenas arquivos .txt são aceitos")
    
    try:
        # Ler conteúdo do arquivo
        content = await file.read()
        content = content.decode('utf-8')
        
        print(f"📁 Arquivo recebido: {file.filename} ({len(content)} caracteres)")
        
        # Parse das mãos
        parsed_hands = parser.parse_file(content)
        
        print(f"🔍 Parser retornou {len(parsed_hands)} mãos")
        
        if not parsed_hands:
            raise HTTPException(status_code=400, detail="Nenhuma mão válida encontrada no arquivo")
        
        processed_hands = []
        tournaments_cache = {}  # Cache para evitar múltiplas consultas
        
        for i, hand_data in enumerate(parsed_hands):
            print(f"📊 Processando mão {i+1}: hand_id={hand_data.get('hand_id')}")
            
            # Verificar se mão já existe
            existing_hand = db.query(Hand).filter(
                Hand.user_id == current_user.id,
                Hand.hand_id == hand_data.get('hand_id')
            ).first()
            
            if existing_hand:
                print(f"⚠️ Mão {hand_data.get('hand_id')} já existe - pulando")
                continue  # Pular mãos duplicadas
            
            # Garantir valores padrão para campos obrigatórios
            hand_id = hand_data.get('hand_id') or f"unknown_{i+1}_{current_user.id}"
            pokerstars_tournament_id = hand_data.get('tournament_id')
            
            # Buscar ou criar torneio
            tournament_db_id = None
            if pokerstars_tournament_id:
                # Usar cache para evitar múltiplas consultas do mesmo torneio
                if pokerstars_tournament_id in tournaments_cache:
                    tournament_db_id = tournaments_cache[pokerstars_tournament_id]
                else:
                    tournament = get_or_create_tournament(db, current_user.id, hand_data)
                    if tournament:
                        tournament_db_id = tournament.id
                        tournaments_cache[pokerstars_tournament_id] = tournament_db_id
            
            # Analisar mão com IA (ou análise básica se IA não disponível)
            try:
                ai_analysis = await ai_service.analyze_hand(hand_data)
            except Exception as e:
                print(f"⚠️ IA indisponível, usando análise básica: {e}")
                ai_analysis = f"""
ANÁLISE BÁSICA (IA indisponível):

Posição: {hand_data.get('hero_position', 'Desconhecida')}
Cartas: {hand_data.get('hero_cards', 'Não identificadas')}
Ação: {hand_data.get('hero_action', 'Não identificada')}

Esta é uma análise básica. Para análise completa com IA, verifique a configuração da API.

RECOMENDAÇÕES GERAIS:
- Analise a posição antes de tomar decisões
- Considere o tamanho do pot e stack sizes
- Observe os padrões dos oponentes
- Mantenha disciplina com bankroll management

Para análise mais detalhada, configure a integração com OpenRouter.
"""
            
            # Criar registro no banco
            db_hand = Hand(
                user_id=current_user.id,
                tournament_id=tournament_db_id,  # FK para tabela tournaments
                hand_id=hand_id,
                pokerstars_tournament_id=pokerstars_tournament_id,  # ID original do PokerStars
                table_name=hand_data.get('table_name'),
                date_played=hand_data.get('date_played') or datetime.now(),
                hero_name=hand_data.get('hero_name'),
                hero_position=hand_data.get('hero_position'),
                hero_cards=hand_data.get('hero_cards'),
                hero_action=hand_data.get('hero_action'),
                pot_size=hand_data.get('pot_size'),
                bet_amount=hand_data.get('bet_amount'),
                board_cards=hand_data.get('board_cards'),
                raw_hand=hand_data.get('raw_hand', ''),
                ai_analysis=ai_analysis
            )
            
            db.add(db_hand)
            processed_hands.append(db_hand)
            print(f"✅ Mão {hand_id} adicionada ao banco (torneio_id: {tournament_db_id})")
        
        db.commit()
        
        # Atualizar objetos com IDs
        for hand in processed_hands:
            db.refresh(hand)
        
        print(f"🎉 Upload concluído: {len(processed_hands)} mãos processadas")
        
        return UploadResponse(
            message=f"Processadas {len(processed_hands)} mãos com sucesso",
            hands_processed=len(processed_hands),
            hands=processed_hands
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas das mãos do usuário"""
    
    # Estatísticas básicas
    total_hands = db.query(func.count(Hand.id)).filter(Hand.user_id == current_user.id).scalar()
    
    # Estatísticas por posição
    position_stats = db.query(
        Hand.hero_position,
        func.count(Hand.id).label('count')
    ).filter(
        Hand.user_id == current_user.id,
        Hand.hero_position.isnot(None)
    ).group_by(Hand.hero_position).all()
    
    # Estatísticas por ação
    action_stats = db.query(
        Hand.hero_action,
        func.count(Hand.id).label('count')
    ).filter(
        Hand.user_id == current_user.id,
        Hand.hero_action.isnot(None)
    ).group_by(Hand.hero_action).all()
    
    # Mãos recentes (últimas 10)
    recent_hands = db.query(Hand).filter(
        Hand.user_id == current_user.id
    ).order_by(Hand.created_at.desc()).limit(10).all()
    
    # Análise de gaps (simulada por enquanto)
    gaps_found = 0
    for hand in recent_hands:
        if hand.ai_analysis and ('gap' in hand.ai_analysis.lower() or 'erro' in hand.ai_analysis.lower()):
            gaps_found += 1
    
    return {
        "total_hands": total_hands,
        "gaps_found": gaps_found,
        "gap_percentage": round((gaps_found / total_hands * 100) if total_hands > 0 else 0, 1),
        "position_stats": [{"position": pos, "count": count} for pos, count in position_stats],
        "action_stats": [{"action": action, "count": count} for action, count in action_stats],
        "recent_hands": [
            {
                "id": hand.id,
                "hand_id": hand.hand_id,
                "hero_position": hand.hero_position,
                "hero_cards": hand.hero_cards,
                "hero_action": hand.hero_action,
                "date_played": hand.date_played,
                "has_gap": 'gap' in (hand.ai_analysis or '').lower() or 'erro' in (hand.ai_analysis or '').lower()
            }
            for hand in recent_hands
        ]
    }

@router.get("/history/my-hands", response_model=List[HandSchema])
async def get_my_hands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    order_by: str = Query("date_asc", regex="^(date_asc|date_desc|created_asc|created_desc)$"),
    gap_filter: Optional[str] = Query(None, regex="^(all|ok|gap|error)$"),
    position_filter: Optional[str] = Query(None),
    action_filter: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter histórico de mãos do usuário com filtros e ordenação"""
    
    # Query base
    query = db.query(Hand).filter(Hand.user_id == current_user.id)
    
    # Filtro por gap
    if gap_filter and gap_filter != "all":
        if gap_filter == "ok":
            # Mãos sem gaps (análise não contém palavras de erro)
            query = query.filter(
                ~Hand.ai_analysis.ilike('%gap%'),
                ~Hand.ai_analysis.ilike('%erro%'),
                ~Hand.ai_analysis.ilike('%error%'),
                ~Hand.ai_analysis.ilike('%mistake%')
            )
        elif gap_filter == "gap":
            # Mãos com gaps (análise contém palavras de gap)
            query = query.filter(
                Hand.ai_analysis.ilike('%gap%')
            )
        elif gap_filter == "error":
            # Mãos com erros (análise contém palavras de erro)
            query = query.filter(
                or_(
                    Hand.ai_analysis.ilike('%erro%'),
                    Hand.ai_analysis.ilike('%error%'),
                    Hand.ai_analysis.ilike('%mistake%')
                )
            )
    
    # Filtro por posição
    if position_filter:
        query = query.filter(Hand.hero_position == position_filter)
    
    # Filtro por ação
    if action_filter:
        query = query.filter(Hand.hero_action == action_filter)
    
    # Filtro por data
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Hand.date_played >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Hand.date_played <= date_to_obj)
        except ValueError:
            pass
    
    # Ordenação
    if order_by == "date_asc":
        query = query.order_by(Hand.date_played.asc())
    elif order_by == "date_desc":
        query = query.order_by(Hand.date_played.desc())
    elif order_by == "created_asc":
        query = query.order_by(Hand.created_at.asc())
    elif order_by == "created_desc":
        query = query.order_by(Hand.created_at.desc())
    
    # Aplicar paginação
    hands = query.offset(skip).limit(limit).all()
    
    return hands

@router.get("/history/my-hands/count")
async def get_my_hands_count(
    gap_filter: Optional[str] = Query(None, regex="^(all|ok|gap|error)$"),
    position_filter: Optional[str] = Query(None),
    action_filter: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter contagem total de mãos com filtros aplicados"""
    
    # Query base
    query = db.query(func.count(Hand.id)).filter(Hand.user_id == current_user.id)
    
    # Aplicar os mesmos filtros do endpoint principal
    if gap_filter and gap_filter != "all":
        if gap_filter == "ok":
            query = query.filter(
                ~Hand.ai_analysis.ilike('%gap%'),
                ~Hand.ai_analysis.ilike('%erro%'),
                ~Hand.ai_analysis.ilike('%error%'),
                ~Hand.ai_analysis.ilike('%mistake%')
            )
        elif gap_filter == "gap":
            query = query.filter(Hand.ai_analysis.ilike('%gap%'))
        elif gap_filter == "error":
            query = query.filter(
                or_(
                    Hand.ai_analysis.ilike('%erro%'),
                    Hand.ai_analysis.ilike('%error%'),
                    Hand.ai_analysis.ilike('%mistake%')
                )
            )
    
    if position_filter:
        query = query.filter(Hand.hero_position == position_filter)
    
    if action_filter:
        query = query.filter(Hand.hero_action == action_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Hand.date_played >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Hand.date_played <= date_to_obj)
        except ValueError:
            pass
    
    total = query.scalar()
    return {"total": total}

@router.get("/history/filters/options")
async def get_filter_options(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter opções disponíveis para filtros"""
    
    # Posições disponíveis
    positions = db.query(Hand.hero_position).filter(
        Hand.user_id == current_user.id,
        Hand.hero_position.isnot(None)
    ).distinct().all()
    
    # Ações disponíveis
    actions = db.query(Hand.hero_action).filter(
        Hand.user_id == current_user.id,
        Hand.hero_action.isnot(None)
    ).distinct().all()
    
    return {
        "positions": [pos[0] for pos in positions if pos[0]],
        "actions": [action[0] for action in actions if action[0]],
        "gap_options": [
            {"value": "all", "label": "Todas as mãos"},
            {"value": "ok", "label": "Mãos OK (sem gaps)"},
            {"value": "gap", "label": "Mãos com gaps"},
            {"value": "error", "label": "Mãos com erros"}
        ],
        "order_options": [
            {"value": "date_asc", "label": "Data (mais antiga primeiro)"},
            {"value": "date_desc", "label": "Data (mais recente primeiro)"},
            {"value": "created_asc", "label": "Criação (mais antiga primeiro)"},
            {"value": "created_desc", "label": "Criação (mais recente primeiro)"}
        ]
    }

@router.get("/history/my-hands/{hand_id}", response_model=HandSchema)
async def get_hand_detail(
    hand_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de uma mão específica"""
    hand = db.query(Hand).filter(
        Hand.id == hand_id,
        Hand.user_id == current_user.id
    ).first()
    
    if not hand:
        raise HTTPException(status_code=404, detail="Mão não encontrada")
    
    return hand

@router.delete("/history/my-hands/{hand_id}")
async def delete_hand(
    hand_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deletar uma mão específica"""
    hand = db.query(Hand).filter(
        Hand.id == hand_id,
        Hand.user_id == current_user.id
    ).first()
    
    if not hand:
        raise HTTPException(status_code=404, detail="Mão não encontrada")
    
    db.delete(hand)
    db.commit()
    
    return {"message": "Mão deletada com sucesso"}



@router.get("/replay/{hand_id}")
async def get_hand_replay(
    hand_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter dados da mão para reprodução na mesa virtual"""
    
    # Buscar mão no banco
    hand = db.query(Hand).filter(
        Hand.id == hand_id,
        Hand.user_id == current_user.id
    ).first()
    
    if not hand:
        raise HTTPException(status_code=404, detail="Mão não encontrada")
    
    # Parse avançado da mão para reprodução
    replay_data = parse_hand_for_table_replay(hand.raw_hand)
    
    if not replay_data:
        raise HTTPException(status_code=400, detail="Não foi possível processar a mão para reprodução")
    
    # Adicionar informações adicionais do banco
    replay_data.update({
        'hand_db_id': hand.id,
        'date_played': hand.date_played,
        'ai_analysis': hand.ai_analysis,
        'hero_position_name': hand.hero_position,
        'hero_action_summary': hand.hero_action,
        'pot_size': hand.pot_size,
        'bet_amount': hand.bet_amount,
        'board_cards': hand.board_cards
    })
    
    return replay_data

@router.post("/replay/{hand_id}/analyze-action")
async def analyze_specific_action(
    hand_id: int,
    action_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analisar uma ação específica da mão com IA"""
    
    # Buscar mão no banco
    hand = db.query(Hand).filter(
        Hand.id == hand_id,
        Hand.user_id == current_user.id
    ).first()
    
    if not hand:
        raise HTTPException(status_code=404, detail="Mão não encontrada")
    
    try:
        # Análise específica da ação com contexto
        analysis_prompt = f"""
        Analise esta ação específica no contexto da mão:
        
        Situação:
        - Street: {action_data.get('street', 'unknown')}
        - Jogador: {action_data.get('player', 'unknown')}
        - Ação: {action_data.get('action', 'unknown')}
        - Valor: {action_data.get('amount', 0)}
        - Cartas do herói: {action_data.get('hero_cards', [])}
        - Cartas comunitárias: {action_data.get('community_cards', [])}
        - Posição: {action_data.get('position', 'unknown')}
        - Tamanho do pot: {action_data.get('pot_size', 0)}
        
        Contexto da mão:
        {hand.raw_hand[:500]}...
        
        Forneça uma análise específica desta ação:
        1. A ação foi correta?
        2. Quais eram as alternativas?
        3. Que fatores deveriam ser considerados?
        4. Há algum gap ou erro?
        """
        
        # Usar serviço de IA para análise
        specific_analysis = await ai_service.analyze_custom_prompt(analysis_prompt)
        
        return {
            'action_analysis': specific_analysis,
            'action_context': action_data,
            'recommendations': [
                'Considere o tamanho do pot e odds',
                'Analise a força relativa da mão',
                'Observe padrões dos oponentes',
                'Avalie a posição na mesa'
            ]
        }
        
    except Exception as e:
        # Análise básica se IA não disponível
        return {
            'action_analysis': f"""
            Análise básica da ação:
            
            Ação: {action_data.get('action', 'unknown')} por {action_data.get('amount', 0)}
            Street: {action_data.get('street', 'unknown')}
            
            Para análise detalhada, configure a integração com IA.
            
            Pontos a considerar:
            - Força da mão atual
            - Posição na mesa
            - Tamanho do pot
            - Padrões dos oponentes
            """,
            'action_context': action_data,
            'recommendations': [
                'Configure IA para análise detalhada',
                'Considere fatores básicos de poker',
                'Analise contexto da situação'
            ],
            'error': str(e)
        }

