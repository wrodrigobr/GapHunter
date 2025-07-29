from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.models.database import get_db
from app.models.user import User
from app.models.hand import Hand
from app.models.schemas import Hand as HandSchema, UploadResponse
from app.services.auth import get_current_active_user
from app.utils.poker_parser import PokerStarsParser
from app.services.ai_service import AIAnalysisService

router = APIRouter()
parser = PokerStarsParser()
ai_service = AIAnalysisService()

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
            tournament_id = hand_data.get('tournament_id')
            
            # SOLUÇÃO TEMPORÁRIA: Tratar tournament_id que excede limite de int
            # SQL Server int máximo: 2,147,483,647
            if tournament_id:
                try:
                    tournament_id_int = int(tournament_id)
                    if tournament_id_int > 2147483647:
                        # Se muito grande, usar None (será armazenado no pokerstars_tournament_id)
                        print(f"⚠️ Tournament ID {tournament_id} muito grande para int, usando None")
                        tournament_id = None
                    else:
                        tournament_id = tournament_id_int
                except (ValueError, TypeError):
                    tournament_id = None
            
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
                hand_id=hand_id,
                tournament_id=tournament_id,
                pokerstars_tournament_id=hand_data.get('tournament_id'),  # Valor original como string
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
            print(f"✅ Mão {hand_id} adicionada ao banco")
        
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

@router.get("/history/my-hands", response_model=List[HandSchema])
async def get_my_hands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter histórico de mãos do usuário"""
    hands = db.query(Hand).filter(
        Hand.user_id == current_user.id
    ).order_by(Hand.created_at.desc()).offset(skip).limit(limit).all()
    
    return hands

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

