#!/usr/bin/env python3
"""
Teste para verificar se o erro do Math foi corrigido nos componentes
"""

import os
import sys

def test_math_fix():
    print("🔍 TESTANDO CORREÇÃO DO ERRO MATH")
    print("=" * 40)
    
    # Verificar arquivos que precisam da correção
    files_to_check = [
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.ts",
        "../frontend/src/app/components/poker-table-fullscreen/poker-table-fullscreen.component.ts"
    ]
    
    fixes_found = {
        "poker_replayer": False,
        "poker_table_fullscreen": False
    }
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Arquivo encontrado: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar se Math foi adicionado
                if "Math = Math;" in content:
                    if "poker-replayer" in file_path:
                        fixes_found["poker_replayer"] = True
                        print(f"  ✅ Math adicionado ao PokerReplayerComponent")
                    elif "poker-table-fullscreen" in file_path:
                        fixes_found["poker_table_fullscreen"] = True
                        print(f"  ✅ Math adicionado ao PokerTableFullscreenComponent")
                else:
                    print(f"  ❌ Math não encontrado em {file_path}")
                    
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    print("\n📊 RESUMO DAS CORREÇÕES:")
    print("-" * 30)
    
    if fixes_found["poker_replayer"]:
        print("✅ PokerReplayerComponent corrigido")
    else:
        print("❌ PokerReplayerComponent não corrigido")
    
    if fixes_found["poker_table_fullscreen"]:
        print("✅ PokerTableFullscreenComponent corrigido")
    else:
        print("❌ PokerTableFullscreenComponent não corrigido")
    
    # Verificar se todas as correções foram aplicadas
    all_fixes = all(fixes_found.values())
    
    print("\n🎯 RESULTADO FINAL:")
    if all_fixes:
        print("✅ TODOS OS ERROS MATH FORAM CORRIGIDOS!")
        print("\n📋 CORREÇÕES APLICADAS:")
        print("1. Math = Math; adicionado ao PokerReplayerComponent")
        print("2. Math = Math; adicionado ao PokerTableFullscreenComponent")
        print("3. Templates HTML agora podem usar Math.min() sem erro")
    else:
        print("❌ ALGUNS ERROS MATH NÃO FORAM CORRIGIDOS")
        missing = [key for key, value in fixes_found.items() if not value]
        print(f"Componentes não corrigidos: {', '.join(missing)}")
    
    return all_fixes

if __name__ == "__main__":
    success = test_math_fix()
    sys.exit(0 if success else 1) 