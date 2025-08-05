#!/usr/bin/env python3
"""
Script para executar a migration da tabela hand_actions
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Executa a migration para criar a tabela hand_actions"""
    
    # Caminho para o banco de dados
    db_path = Path(__file__).parent / "gaphunter.db"
    
    # Caminho para o arquivo de migration
    migration_path = Path(__file__).parent / "migrations" / "003_add_hand_actions_table.sql"
    
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    if not migration_path.exists():
        print(f"❌ Arquivo de migration não encontrado: {migration_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔗 Conectado ao banco: {db_path}")
        
        # Ler o arquivo de migration
        with open(migration_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print(f"📄 Migration carregada: {migration_path}")
        
        # Executar a migration
        print("🚀 Executando migration...")
        
        # Dividir o SQL em comandos individuais
        commands = migration_sql.split(';')
        
        for i, command in enumerate(commands):
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    print(f"✅ Comando {i+1} executado com sucesso")
                except sqlite3.Error as e:
                    if "already exists" in str(e):
                        print(f"⚠️  Comando {i+1}: {e}")
                    else:
                        print(f"❌ Erro no comando {i+1}: {e}")
                        raise
        
        # Commit das alterações
        conn.commit()
        print("💾 Alterações salvas no banco")
        
        # Verificar se a tabela foi criada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hand_actions'")
        if cursor.fetchone():
            print("✅ Tabela hand_actions criada com sucesso!")
        else:
            print("❌ Tabela hand_actions não foi criada")
            return False
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(hand_actions)")
        columns = cursor.fetchall()
        print("\n📋 Estrutura da tabela hand_actions:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar se a view foi criada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='hand_actions_summary'")
        if cursor.fetchone():
            print("✅ View hand_actions_summary criada com sucesso!")
        else:
            print("⚠️  View hand_actions_summary não foi criada")
        
        conn.close()
        print("\n🎉 Migration executada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migration: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Iniciando migration da tabela hand_actions...")
    success = run_migration()
    
    if success:
        print("\n✅ Migration concluída com sucesso!")
        print("📝 A tabela hand_actions está pronta para uso.")
        print("🔗 Agora você pode armazenar ações individuais de cada mão com identificação da street.")
    else:
        print("\n❌ Migration falhou!")
        exit(1) 