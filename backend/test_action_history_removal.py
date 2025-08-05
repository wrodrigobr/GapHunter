#!/usr/bin/env python3
"""
Teste para verificar se o Action History foi removido do componente RIROPO
"""

import os
import sys

def test_action_history_removal():
    print("🔍 TESTANDO REMOÇÃO DO ACTION HISTORY")
    print("=" * 45)
    
    # Verificar arquivos modificados
    files_to_check = [
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.html",
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.scss"
    ]
    
    removal_status = {
        "html_removed": False,
        "css_removed": False,
        "layout_simplified": False
    }
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Arquivo encontrado: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if "poker-replayer.component.html" in file_path:
                    # Verificar se Action History foi removido do HTML
                    if "action-history" not in content and "left-panel" not in content:
                        removal_status["html_removed"] = True
                        print(f"  ✅ Action History removido do HTML")
                    else:
                        print(f"  ❌ Action History ainda presente no HTML")
                
                elif "poker-replayer.component.scss" in file_path:
                    # Verificar se estilos do Action History foram removidos
                    if ".action-history" not in content and ".left-panel" not in content:
                        removal_status["css_removed"] = True
                        print(f"  ✅ Estilos do Action History removidos")
                    else:
                        print(f"  ❌ Estilos do Action History ainda presentes")
                    
                    # Verificar se layout foi simplificado
                    if "Layout simplificado" in content and "min-height: 120px" in content:
                        removal_status["layout_simplified"] = True
                        print(f"  ✅ Layout simplificado implementado")
                    else:
                        print(f"  ❌ Layout não foi simplificado")
                        
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    print("\n📊 RESUMO DA REMOÇÃO:")
    print("-" * 30)
    
    if removal_status["html_removed"]:
        print("✅ Action History removido do HTML")
    else:
        print("❌ Action History não removido do HTML")
    
    if removal_status["css_removed"]:
        print("✅ Estilos do Action History removidos")
    else:
        print("❌ Estilos do Action History não removidos")
    
    if removal_status["layout_simplified"]:
        print("✅ Layout simplificado implementado")
    else:
        print("❌ Layout não foi simplificado")
    
    # Verificar se todas as remoções foram aplicadas
    all_removed = all(removal_status.values())
    
    print("\n🎯 RESULTADO FINAL:")
    if all_removed:
        print("✅ ACTION HISTORY REMOVIDO COM SUCESSO!")
        print("\n📋 MELHORIAS APLICADAS:")
        print("1. Action History removido do template HTML")
        print("2. Estilos CSS do Action History removidos")
        print("3. Layout simplificado com controles centralizados")
        print("4. Altura reduzida de 200px para 120px")
        print("5. Mais espaço para a mesa de poker")
    else:
        print("❌ ALGUMAS REMOÇÕES NÃO FORAM APLICADAS")
        missing = [key for key, value in removal_status.items() if not value]
        print(f"Remoções faltantes: {', '.join(missing)}")
    
    return all_removed

if __name__ == "__main__":
    success = test_action_history_removal()
    sys.exit(0 if success else 1) 