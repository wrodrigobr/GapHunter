#!/usr/bin/env python3
"""
Script para criar um usuário de teste
"""

import sys
import os

# Adicionar o diretório atual ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.models.database import SessionLocal
from app.models.user import User
from app.services.auth import get_password_hash

def create_test_user():
    """Cria um usuário de teste"""
    print("🔧 CRIANDO USUÁRIO DE TESTE")
    print("=" * 30)
    
    db = SessionLocal()
    
    try:
        # Verificar se o usuário já existe
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if existing_user:
            print("✅ Usuário de teste já existe")
            print(f"📧 Email: {existing_user.email}")
            print(f"🆔 ID: {existing_user.id}")
            return True
        
        # Criar novo usuário
        hashed_password = get_password_hash("test123")
        
        new_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("✅ Usuário de teste criado com sucesso")
        print(f"📧 Email: {new_user.email}")
        print(f"🆔 ID: {new_user.id}")
        print("🔑 Senha: test123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 