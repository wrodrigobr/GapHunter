from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.models.schemas import Token, UserCreate, User as UserSchema
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    # Verificar se usuário já existe
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username ou email já cadastrado"
        )
    
    # Criar novo usuário
    hashed_password = get_password_hash(user.password)
    
    # SOLUÇÃO TEMPORÁRIA: Tratar campo nickname que pode não existir no banco
    user_data = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "poker_experience": user.poker_experience,
        "preferred_games": user.preferred_games,
        "main_stakes": user.main_stakes,
        "poker_goals": user.poker_goals,
        "country": user.country,
        "timezone": user.timezone
    }
    
    # Adicionar nickname apenas se o campo existir no banco
    try:
        db_user = User(**user_data, nickname=user.nickname)
    except Exception as e:
        print(f"⚠️ Campo nickname não existe no banco, criando sem ele: {e}")
        db_user = User(**user_data)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Criar token de acesso para o usuário recém-criado
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login do usuário"""
    try:
        print(f"🚀 Iniciando login para: {form_data.username}")
        
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            print(f"❌ Falha na autenticação para: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✅ Usuário autenticado: {user.username}")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        print(f"🎫 Token criado para: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-raise HTTP exceptions (como 401)
        raise
    except Exception as e:
        print(f"💥 ERRO INTERNO no login: {str(e)}")
        print(f"💥 Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Obter informações do usuário atual"""
    return current_user

