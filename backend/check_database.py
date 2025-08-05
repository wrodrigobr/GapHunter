#!/usr/bin/env python3
"""
Script para verificar a estrutura e dados do banco
"""

import sqlite3
from pathlib import Path

def check_database():
    """Verifica a estrutura e dados do banco"""
    
    db_path = Path(__file__).parent / "gaphunter.db"
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 VERIFICANDO BANCO DE DADOS")
        print("=" * 40)
        
        # 1. Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 2. Verificar dados em cada tabela
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📊 {table_name}: {count} registros")
        
        # 3. Verificar estrutura da tabela hands
        if 'hands' in [t[0] for t in tables]:
            print("\n📋 Estrutura da tabela hands:")
            cursor.execute("PRAGMA table_info(hands)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) - Nullable: {col[3]}")
        
        # 4. Verificar estrutura da tabela hand_actions
        if 'hand_actions' in [t[0] for t in tables]:
            print("\n📋 Estrutura da tabela hand_actions:")
            cursor.execute("PRAGMA table_info(hand_actions)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) - Nullable: {col[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_database() 