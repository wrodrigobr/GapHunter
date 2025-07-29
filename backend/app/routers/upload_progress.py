from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import asyncio
import uuid
from datetime import datetime

from app.models.database import get_db
from app.models.user import User
from app.models.hand import Hand
from app.models.tournament import Tournament
from app.models.schemas import UploadResponse
from app.services.auth import get_current_active_user
from app.utils.poker_parser import PokerStarsParser
from app.services.ai_service import AIAnalysisService

router = APIRouter()
parser = PokerStarsParser()
ai_service = AIAnalysisService()

# Armazenar progresso de uploads em memória (em produção, usar Redis)
upload_progress: Dict[str, Dict[str, Any]] = {}

@router.post("/upload-async")
async def upload_hand_history_async(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Inicia upload assíncrono e retorna ID para acompanhar progresso"""
    
    # Verificar se é arquivo .txt
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Apenas arquivos .txt são aceitos")
    
    # Gerar ID único para este upload
    upload_id = str(uuid.uuid4())
    
    # Inicializar progresso
    upload_progress[upload_id] = {
        "status": "starting",
        "progress": 0,
        "total_hands": 0,
        "processed_hands": 0,
        "current_hand": "",
        "message": "Iniciando análise...",
        "errors": [],
        "completed": False,
        "result": None
    }
    
    # Processar arquivo em background
    asyncio.create_task(process_upload_background(
        upload_id, file, current_user.id
    ))
    
    return {"upload_id": upload_id, "message": "Upload iniciado"}

async def process_upload_background(
    upload_id: str, 
    file: UploadFile, 
    user_id: int
):
    """Processa upload em background com atualizações de progresso"""
    
    db = None
    try:
        print(f"🚀 Iniciando processamento background para upload {upload_id}")
        
        # Criar nova sessão para esta tarefa
        from app.models.database import SessionLocal
        db = SessionLocal()
        
        # Atualizar status
        upload_progress[upload_id]["status"] = "reading_file"
        upload_progress[upload_id]["message"] = "Lendo arquivo..."
        print(f"📖 Status atualizado: reading_file")
        
        # Ler conteúdo do arquivo
        content = await file.read()
        content = content.decode('utf-8')
        
        print(f"📁 Arquivo lido: {len(content)} caracteres")
        
        upload_progress[upload_id]["message"] = f"Arquivo lido: {len(content)} caracteres"
        upload_progress[upload_id]["progress"] = 10
        
        # Parse das mãos
        upload_progress[upload_id]["status"] = "parsing"
        upload_progress[upload_id]["message"] = "Analisando estrutura do arquivo..."
        print(f"🔍 Iniciando parse do arquivo...")
        
        parsed_hands = parser.parse_file(content)
        print(f"🔍 Parse concluído: {len(parsed_hands)} mãos encontradas")
        
        if not parsed_hands:
            upload_progress[upload_id]["status"] = "error"
            upload_progress[upload_id]["message"] = "Nenhuma mão válida encontrada no arquivo"
            upload_progress[upload_id]["errors"].append("Arquivo não contém mãos válidas")
            print(f"❌ Nenhuma mão válida encontrada")
            return
        
        total_hands = len(parsed_hands)
        upload_progress[upload_id]["total_hands"] = total_hands
        upload_progress[upload_id]["progress"] = 20
        upload_progress[upload_id]["message"] = f"Encontradas {total_hands} mãos para processar"
        upload_progress[upload_id]["status"] = "processing"
        print(f"📊 Iniciando processamento de {total_hands} mãos")
        
        processed_hands = []
        tournaments_cache = {}  # Cache para evitar múltiplas consultas
        
        for i, hand_data in enumerate(parsed_hands):
            try:
                # Atualizar progresso
                progress_percent = 20 + int((i / total_hands) * 70)  # 20-90%
                upload_progress[upload_id]["progress"] = progress_percent
                upload_progress[upload_id]["processed_hands"] = i
                upload_progress[upload_id]["current_hand"] = f"Mão #{hand_data.get('hand_id', 'unknown')}"
                upload_progress[upload_id]["message"] = f"Processando mão {i+1}/{total_hands}"
                
                if i % 5 == 0:  # Log a cada 5 mãos
                    print(f"📊 Processando mão {i+1}/{total_hands}")
                
                # Verificar se mão já existe
                existing_hand = db.query(Hand).filter(
                    Hand.user_id == user_id,
                    Hand.hand_id == hand_data.get('hand_id')
                ).first()
                
                if existing_hand:
                    upload_progress[upload_id]["message"] = f"Mão {i+1}/{total_hands} (duplicada - pulando)"
                    continue
                
                # Garantir valores padrão para campos obrigatórios
            hand_id = hand_data.get('hand_id') or f"unknown_{i+1}_{user_id}"
            pokerstars_tournament_id = hand_data.get('tournament_id')
            
            # Buscar ou criar torneio
            tournament_db_id = None
            if pokerstars_tournament_id:
                # Usar cache para evitar múltiplas consultas do mesmo torneio
                if pokerstars_tournament_id in tournaments_cache:
                    tournament_db_id = tournaments_cache[pokerstars_tournament_id]
                else:
                    # Buscar torneio existente
                    existing_tournament = db.query(Tournament).filter(
                        Tournament.user_id == user_id,
                        Tournament.tournament_id == pokerstars_tournament_id
                    ).first()
                    
                    if existing_tournament:
                        tournament_db_id = existing_tournament.id
                        tournaments_cache[pokerstars_tournament_id] = tournament_db_id
                    else:
                        # Criar novo torneio
                        try:
                            new_tournament = Tournament(
                                user_id=user_id,
                                tournament_id=pokerstars_tournament_id,
                                name=f"Torneio {pokerstars_tournament_id}",
                                buy_in=0.0,
                                date_played=hand_data.get('date_played') or datetime.now(),
                                platform="PokerStars"
                            )
                            
                            db.add(new_tournament)
                            db.flush()  # Para obter o ID sem fazer commit
                            
                            tournament_db_id = new_tournament.id
                            tournaments_cache[pokerstars_tournament_id] = tournament_db_id
                            print(f"✅ Torneio {pokerstars_tournament_id} criado com ID {tournament_db_id}")
                            
                        except Exception as e:
                            print(f"❌ Erro ao criar torneio {pokerstars_tournament_id}: {e}")
                            tournament_db_id = None
                
                # Análise básica (sem IA por enquanto para debug)
                ai_analysis = f"""
ANÁLISE BÁSICA:

Posição: {hand_data.get('hero_position', 'Desconhecida')}
Cartas: {hand_data.get('hero_cards', 'Não identificadas')}
Ação: {hand_data.get('hero_action', 'Não identificada')}

Esta é uma análise básica para debug.
"""
                
                # Criar registro no banco
                db_hand = Hand(
                    user_id=user_id,
                    hand_id=hand_id,
                    tournament_id=tournament_db_id,  # FK para tabela tournaments
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
                
                # Commit a cada 5 mãos para debug
                if (i + 1) % 5 == 0:
                    db.commit()
                    upload_progress[upload_id]["message"] = f"Salvando progresso... ({i+1}/{total_hands})"
                    print(f"💾 Commit realizado: {i+1} mãos")
                
            except Exception as e:
                error_msg = f"Erro na mão {i+1}: {str(e)}"
                upload_progress[upload_id]["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        
        # Commit final
        print(f"💾 Commit final...")
        db.commit()
        
        # Atualizar objetos com IDs
        for hand in processed_hands:
            db.refresh(hand)
        
        # Finalizar
        upload_progress[upload_id]["status"] = "completed"
        upload_progress[upload_id]["progress"] = 100
        upload_progress[upload_id]["processed_hands"] = len(processed_hands)
        upload_progress[upload_id]["completed"] = True
        upload_progress[upload_id]["message"] = f"Concluído! {len(processed_hands)} mãos processadas"
        upload_progress[upload_id]["result"] = {
            "hands_processed": len(processed_hands),
            "total_found": total_hands,
            "duplicates_skipped": total_hands - len(processed_hands)
        }
        
        print(f"✅ Upload {upload_id} concluído: {len(processed_hands)} mãos processadas")
        
    except Exception as e:
        upload_progress[upload_id]["status"] = "error"
        upload_progress[upload_id]["message"] = f"Erro durante processamento: {str(e)}"
        upload_progress[upload_id]["errors"].append(str(e))
        print(f"❌ Erro no upload {upload_id}: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
    finally:
        if db:
            db.close()
            print(f"🔒 Sessão do banco fechada para upload {upload_id}")

@router.get("/upload-progress/{upload_id}")
async def get_upload_progress(upload_id: str):
    """Retorna progresso atual do upload"""
    
    if upload_id not in upload_progress:
        raise HTTPException(status_code=404, detail="Upload não encontrado")
    
    return upload_progress[upload_id]

@router.get("/debug/uploads")
async def debug_uploads():
    """Debug: Lista todos os uploads em progresso"""
    return {
        "total_uploads": len(upload_progress),
        "uploads": {k: v for k, v in upload_progress.items()}
    }

@router.post("/debug/test-progress")
async def test_progress():
    """Debug: Cria um upload de teste para verificar o sistema"""
    
    upload_id = str(uuid.uuid4())
    
    # Inicializar progresso de teste
    upload_progress[upload_id] = {
        "status": "starting",
        "progress": 0,
        "total_hands": 10,
        "processed_hands": 0,
        "current_hand": "",
        "message": "Teste iniciado...",
        "errors": [],
        "completed": False,
        "result": None
    }
    
    # Simular progresso em background
    asyncio.create_task(simulate_progress(upload_id))
    
    return {"upload_id": upload_id, "message": "Teste iniciado"}

async def simulate_progress(upload_id: str):
    """Simula progresso para teste"""
    try:
        for i in range(10):
            await asyncio.sleep(1)  # Aguardar 1 segundo
            
            upload_progress[upload_id]["progress"] = (i + 1) * 10
            upload_progress[upload_id]["processed_hands"] = i + 1
            upload_progress[upload_id]["current_hand"] = f"Teste #{i + 1}"
            upload_progress[upload_id]["message"] = f"Processando teste {i + 1}/10"
            upload_progress[upload_id]["status"] = "processing"
            
            print(f"🧪 Teste {upload_id}: {i + 1}/10")
        
        # Finalizar teste
        upload_progress[upload_id]["status"] = "completed"
        upload_progress[upload_id]["progress"] = 100
        upload_progress[upload_id]["completed"] = True
        upload_progress[upload_id]["message"] = "Teste concluído!"
        upload_progress[upload_id]["result"] = {
            "hands_processed": 10,
            "total_found": 10,
            "duplicates_skipped": 0
        }
        
        print(f"✅ Teste {upload_id} concluído")
        
    except Exception as e:
        upload_progress[upload_id]["status"] = "error"
        upload_progress[upload_id]["message"] = f"Erro no teste: {str(e)}"
        print(f"❌ Erro no teste {upload_id}: {str(e)}")

@router.get("/upload-stream/{upload_id}")
async def stream_upload_progress(upload_id: str):
    """Stream de progresso em tempo real usando Server-Sent Events"""
    
    if upload_id not in upload_progress:
        raise HTTPException(status_code=404, detail="Upload não encontrado")
    
    async def generate_progress_stream():
        while upload_id in upload_progress:
            progress_data = upload_progress[upload_id]
            
            # Enviar dados no formato SSE
            yield f"data: {json.dumps(progress_data)}\n\n"
            
            # Se completou ou deu erro, parar stream
            if progress_data.get("completed") or progress_data.get("status") == "error":
                break
            
            # Aguardar 1 segundo antes da próxima atualização
            await asyncio.sleep(1)
        
        # Limpar dados após 5 minutos
        await asyncio.sleep(300)
        if upload_id in upload_progress:
            del upload_progress[upload_id]
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

