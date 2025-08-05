#!/usr/bin/env python3
"""
Verificar estrutura da tabela users
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_users_table():
    """Verifica a estrutura da tabela users"""
    print("🔍 VERIFICANDO ESTRUTURA DA TABELA USERS")
    print("=" * 45)
    
    try:
        # Conectar com SQLite
        engine = create_engine("sqlite:///gaphunter.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar estrutura da tabela users
        result = session.execute(text("PRAGMA table_info(users)"))
        columns = [row for row in result]
        
        print("📊 ESTRUTURA DA TABELA USERS:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]}) - Not Null: {col[3]} - Default: {col[4]}")
            
        # Verificar se existem usuários
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        users_count = result.fetchone()[0]
        print(f"\n📊 Total de usuários: {users_count}")
        
        if users_count > 0:
            print("\n📋 PRIMEIROS 5 USUÁRIOS:")
            result = session.execute(text("SELECT id, username, email FROM users LIMIT 5"))
            users = [row for row in result]
            for user in users:
                print(f"  • ID: {user[0]} - Username: {user[1]} - Email: {user[2]}")
                
        session.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_users_table() 