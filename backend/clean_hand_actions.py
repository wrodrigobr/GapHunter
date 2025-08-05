#!/usr/bin/env python3
"""
Script para limpar a tabela hand_actions e economizar espaço no banco.
Executar apenas se você tem certeza de que quer remover todos os dados de ações.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import SessionLocal
from app.models.hand_action import HandAction
from sqlalchemy import text

def clean_hand_actions():
    """Remove todos os registros da tabela hand_actions"""
    
    db = SessionLocal()
    try:
        # Contar registros antes
        count_before = db.query(HandAction).count()
        print(f"📊 Registros na tabela hand_actions antes da limpeza: {count_before}")
        
        if count_before == 0:
            print("✅ Tabela hand_actions já está vazia")
            return
        
        # Confirmar com o usuário
        confirm = input(f"⚠️  Tem certeza que quer remover {count_before} registros da tabela hand_actions? (s/N): ")
        if confirm.lower() != 's':
            print("❌ Operação cancelada")
            return
        
        # Remover todos os registros
        db.query(HandAction).delete()
        db.commit()
        
        # Verificar se foi removido
        count_after = db.query(HandAction).count()
        print(f"✅ Limpeza concluída! Registros restantes: {count_after}")
        
        # Calcular espaço economizado (aproximado)
        # Assumindo ~100 bytes por registro
        space_saved_mb = (count_before * 100) / (1024 * 1024)
        print(f"💾 Espaço economizado (aproximado): {space_saved_mb:.2f} MB")
        
    except Exception as e:
        print(f"❌ Erro durante a limpeza: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Script de limpeza da tabela hand_actions")
    print("=" * 50)
    clean_hand_actions() 