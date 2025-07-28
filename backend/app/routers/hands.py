from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
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
        
        # Parse das mãos
        parsed_hands = parser.parse_file(content)
        
        if not parsed_hands:
            raise HTTPException(status_code=400, detail="Nenhuma mão válida encontrada no arquivo")
        
        processed_hands = []
        
        for hand_data in parsed_hands:
            # Verificar se mão já existe
            existing_hand = db.query(Hand).filter(
                Hand.user_id == current_user.id,
                Hand.hand_id == hand_data['hand_id']
            ).first()
            
            if existing_hand:
                continue  # Pular mãos duplicadas
            
            # Analisar mão com IA
            ai_analysis = await ai_service.analyze_hand(hand_data)
            
            # Criar registro no banco
            db_hand = Hand(
                user_id=current_user.id,
                hand_id=hand_data['hand_id'],
                tournament_id=hand_data['tournament_id'],
                table_name=hand_data['table_name'],
                date_played=hand_data['date_played'],
                hero_name=hand_data['hero_name'],
                hero_position=hand_data['hero_position'],
                hero_cards=hand_data['hero_cards'],
                hero_action=hand_data['hero_action'],
                pot_size=hand_data['pot_size'],
                bet_amount=hand_data['bet_amount'],
                board_cards=hand_data['board_cards'],
                raw_hand=hand_data['raw_hand'],
                ai_analysis=ai_analysis
            )
            
            db.add(db_hand)
            processed_hands.append(db_hand)
        
        db.commit()
        
        # Atualizar objetos com IDs
        for hand in processed_hands:
            db.refresh(hand)
        
        return UploadResponse(
            message=f"Processadas {len(processed_hands)} mãos com sucesso",
            hands_processed=len(processed_hands),
            hands=processed_hands
        )
        
    except Exception as e:
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

