from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.models.database import get_db
from app.models.user import User
from app.models.schemas import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    try:
        # Procurar por username ou email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        print(f"🔍 Buscando usuário: {username} - Encontrado: {'Sim' if user else 'Não'}")
        return user
    except Exception as e:
        print(f"❌ Erro ao buscar usuário {username}: {str(e)}")
        return None

def authenticate_user(db: Session, username: str, password: str):
    try:
        print(f"🔐 Tentativa de autenticação para: {username}")
        user = get_user(db, username)
        if not user:
            print(f"❌ Usuário {username} não encontrado")
            return False
        
        print(f"✅ Usuário {username} encontrado, verificando senha...")
        if not verify_password(password, user.hashed_password):
            print(f"❌ Senha incorreta para usuário {username}")
            return False
        
        print(f"✅ Autenticação bem-sucedida para usuário {username}")
        return user
    except Exception as e:
        print(f"❌ Erro durante autenticação de {username}: {str(e)}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

