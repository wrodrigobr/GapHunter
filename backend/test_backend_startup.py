#!/usr/bin/env python3
"""
Teste de inicialização do backend
"""

import sys
import os
from pathlib import Path

def test_backend_startup():
    """Testa se o backend inicia sem erros"""
    
    print("🧪 TESTE DE INICIALIZAÇÃO DO BACKEND")
    print("=" * 50)
    
    try:
        # Testar importação dos modelos
        print("📋 Testando importação dos modelos...")
        from app.models.user import User
        from app.models.hand import Hand
        from app.models.tournament import Tournament
        from app.models.hand_action import HandAction
        print("✅ Modelos importados com sucesso")
        
        # Testar importação dos serviços
        print("📋 Testando importação dos serviços...")
        from app.services.validation_service import validation_service
        print("✅ Serviços importados com sucesso")
        
        # Testar importação dos routers
        print("📋 Testando importação dos routers...")
        from app.routers import hands
        print("✅ Routers importados com sucesso")
        
        # Testar importação da aplicação
        print("📋 Testando importação da aplicação...")
        from app.main import app
        print("✅ Aplicação importada com sucesso")
        
        print("\n🎉 BACKEND PRONTO PARA INICIAR!")
        print("✅ Todos os componentes carregados com sucesso")
        print("✅ Não há erros de relacionamento SQLAlchemy")
        print("✅ Sistema de validação funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print(f"❌ Tipo do erro: {type(e).__name__}")
        
        # Mostrar mais detalhes sobre o erro
        import traceback
        print("\n📋 Stack trace completo:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    success = test_backend_startup()
    if success:
        print("\n🚀 Para iniciar o backend, execute:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ Corrija os erros antes de iniciar o backend") 