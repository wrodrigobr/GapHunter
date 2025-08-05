#!/usr/bin/env python3
"""
Teste para verificar se as melhorias dos botões de controle foram implementadas
"""

import os
import sys

def test_button_improvements():
    print("🔍 TESTANDO MELHORIAS DOS BOTÕES DE CONTROLE")
    print("=" * 50)
    
    # Verificar arquivos modificados
    files_to_check = [
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.html",
        "../frontend/src/app/components/poker-replayer/poker-replayer.component.scss",
        "../frontend/src/index.html"
    ]
    
    improvements_found = {
        "font_awesome_added": False,
        "better_icons": False,
        "larger_buttons": False,
        "fullscreen_repositioned": False,
        "speed_buttons": False,
        "better_styling": False
    }
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Arquivo encontrado: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if "index.html" in file_path:
                    # Verificar se Font Awesome foi adicionado
                    if "font-awesome" in content:
                        improvements_found["font_awesome_added"] = True
                        print(f"  ✅ Font Awesome adicionado")
                    else:
                        print(f"  ❌ Font Awesome não encontrado")
                
                elif "poker-replayer.component.html" in file_path:
                    # Verificar ícones melhores
                    if "fas fa-" in content and "fa-redo" in content:
                        improvements_found["better_icons"] = True
                        print(f"  ✅ Ícones Font Awesome implementados")
                    else:
                        print(f"  ❌ Ícones não melhorados")
                    
                    # Verificar botões de velocidade
                    if "speed-btn" in content and "speed-buttons" in content:
                        improvements_found["speed_buttons"] = True
                        print(f"  ✅ Botões de velocidade implementados")
                    else:
                        print(f"  ❌ Botões de velocidade não implementados")
                    
                    # Verificar fullscreen reposicionado
                    if "fullscreen-control" in content and "Canto superior direito" in content:
                        improvements_found["fullscreen_repositioned"] = True
                        print(f"  ✅ Fullscreen reposicionado")
                    else:
                        print(f"  ❌ Fullscreen não reposicionado")
                
                elif "poker-replayer.component.scss" in file_path:
                    # Verificar botões maiores
                    if "width: 50px" in content and "height: 50px" in content:
                        improvements_found["larger_buttons"] = True
                        print(f"  ✅ Botões maiores implementados")
                    else:
                        print(f"  ❌ Botões não aumentados")
                    
                    # Verificar estilos melhores
                    if "border-radius: 10px" in content and "transform: translateY(-3px)" in content:
                        improvements_found["better_styling"] = True
                        print(f"  ✅ Estilos melhorados implementados")
                    else:
                        print(f"  ❌ Estilos não melhorados")
                        
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    print("\n📊 RESUMO DAS MELHORIAS:")
    print("-" * 30)
    
    if improvements_found["font_awesome_added"]:
        print("✅ Font Awesome adicionado")
    else:
        print("❌ Font Awesome não adicionado")
    
    if improvements_found["better_icons"]:
        print("✅ Ícones Font Awesome implementados")
    else:
        print("❌ Ícones não melhorados")
    
    if improvements_found["larger_buttons"]:
        print("✅ Botões maiores implementados")
    else:
        print("❌ Botões não aumentados")
    
    if improvements_found["fullscreen_repositioned"]:
        print("✅ Fullscreen reposicionado")
    else:
        print("❌ Fullscreen não reposicionado")
    
    if improvements_found["speed_buttons"]:
        print("✅ Botões de velocidade implementados")
    else:
        print("❌ Botões de velocidade não implementados")
    
    if improvements_found["better_styling"]:
        print("✅ Estilos melhorados implementados")
    else:
        print("❌ Estilos não melhorados")
    
    # Verificar se todas as melhorias foram aplicadas
    all_improvements = all(improvements_found.values())
    
    print("\n🎯 RESULTADO FINAL:")
    if all_improvements:
        print("✅ TODAS AS MELHORIAS DOS BOTÕES FORAM IMPLEMENTADAS!")
        print("\n📋 MELHORIAS APLICADAS:")
        print("1. Font Awesome adicionado para ícones profissionais")
        print("2. Botões maiores (50x50px) para melhor usabilidade")
        print("3. Ícones Font Awesome em vez de emojis")
        print("4. Fullscreen reposicionado para canto superior direito")
        print("5. Botões de velocidade em vez de select")
        print("6. Efeitos hover e animações melhoradas")
        print("7. Cores diferenciadas para botões especiais")
    else:
        print("❌ ALGUMAS MELHORIAS NÃO FORAM APLICADAS")
        missing = [key for key, value in improvements_found.items() if not value]
        print(f"Melhorias faltantes: {', '.join(missing)}")
    
    return all_improvements

if __name__ == "__main__":
    success = test_button_improvements()
    sys.exit(0 if success else 1) 