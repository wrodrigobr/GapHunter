#!/usr/bin/env python3
"""
Verificar estrutura do banco de dados
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_database_structure():
    """Verifica a estrutura do banco de dados"""
    print("🔍 VERIFICANDO ESTRUTURA DO BANCO DE DADOS")
    print("=" * 45)
    
    try:
        # Conectar com SQLite
        engine = create_engine("sqlite:///gaphunter.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar tabelas
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print(f"📋 Tabelas encontradas: {tables}")
        
        # Verificar estrutura da tabela hands
        if 'hands' in tables:
            print("\n📊 ESTRUTURA DA TABELA HANDS:")
            result = session.execute(text("PRAGMA table_info(hands)"))
            columns = [row for row in result]
            for col in columns:
                print(f"  • {col[1]} ({col[2]})")
                
        # Verificar dados na tabela hands
        result = session.execute(text("SELECT COUNT(*) FROM hands"))
        hands_count = result.fetchone()[0]
        print(f"\n📊 Total de mãos na tabela hands: {hands_count}")
        
        if hands_count > 0:
            print("\n📋 ÚLTIMAS 5 MÃOS:")
            result = session.execute(text("SELECT hand_id, hero_position, hero_cards, date_played FROM hands ORDER BY id DESC LIMIT 5"))
            hands = [row for row in result]
            for hand in hands:
                print(f"  • Hand #{hand[0]} - {hand[1]} - {hand[2]} - {hand[3]}")
                
        session.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_database_structure() 