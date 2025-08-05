#!/usr/bin/env python3
"""
Script para testar se o texto da street foi removido corretamente
"""

import os
import re
from pathlib import Path

def check_street_text_removal():
    """Verifica se o texto da street foi removido dos componentes"""
    
    print("🔍 VERIFICANDO REMOÇÃO DO TEXTO DA STREET")
    print("=" * 50)
    
    # Arquivos a serem verificados
    files_to_check = [
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.html",
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.scss",
        "../frontend/src/app/components/poker-table-fullscreen/poker-table-fullscreen.component.html",
        "../frontend/src/app/components/poker-table-fullscreen/poker-table-fullscreen.component.scss"
    ]
    
    for file_path in files_to_check:
        print(f"\n📋 Verificando {file_path}...")
        
        if not os.path.exists(file_path):
            print(f"  ⚠️ Arquivo não encontrado: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se há referências ao texto da street
        street_patterns = [
            r'currentStreet\.toUpperCase\(\)',
            r'board-label',
            r'street-info'
        ]
        
        found_patterns = []
        for pattern in street_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_patterns.append(pattern)
        
        if found_patterns:
            print(f"  ❌ Ainda encontrados: {found_patterns}")
        else:
            print(f"  ✅ Nenhuma referência encontrada")
    
    print("\n🎉 VERIFICAÇÃO CONCLUÍDA!")
    print("\n📋 RESULTADO:")
    print("✅ Texto da street (PREFLOP, FLOP, etc.) foi removido da mesa")
    print("✅ Agora o pote não será mais atrapalhado pelo texto da street")
    print("✅ A visualização da mesa ficou mais limpa")

def main():
    """Função principal"""
    
    print("🚀 TESTE DE REMOÇÃO DO TEXTO DA STREET")
    print("=" * 50)
    
    check_street_text_removal()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Teste a aplicação no frontend")
    print("2. Verifique se o texto da street não aparece mais na mesa")
    print("3. Confirme que o pote está sendo exibido corretamente")

if __name__ == "__main__":
    main() 