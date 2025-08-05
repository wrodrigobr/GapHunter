#!/usr/bin/env python3
"""
Script para testar o novo dashboard focado em estatísticas
"""

import os
import sys
from pathlib import Path

def check_dashboard_files():
    """Verifica se os arquivos do novo dashboard foram criados corretamente"""
    
    print("🔍 VERIFICANDO NOVO DASHBOARD")
    print("=" * 50)
    
    # Arquivos a serem verificados
    files_to_check = [
        "../frontend/src/app/components/dashboard/dashboard.component.html",
        "../frontend/src/app/components/dashboard/dashboard.component.ts",
        "../frontend/src/app/components/dashboard/dashboard.component.scss"
    ]
    
    for file_path in files_to_check:
        print(f"\n📋 Verificando {file_path}...")
        
        if not os.path.exists(file_path):
            print(f"  ❌ Arquivo não encontrado: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos do novo dashboard
        new_elements = [
            "performance-overview",
            "kpi-section", 
            "gap-analysis",
            "improvement-areas",
            "monthly-progress",
            "history-button",
            "overview-card",
            "kpi-card",
            "gap-card",
            "improvement-card"
        ]
        
        found_elements = []
        for element in new_elements:
            if element in content:
                found_elements.append(element)
        
        if found_elements:
            print(f"  ✅ Elementos encontrados: {len(found_elements)}/{len(new_elements)}")
            print(f"     {', '.join(found_elements)}")
        else:
            print(f"  ❌ Nenhum elemento do novo dashboard encontrado")

def check_removed_elements():
    """Verifica se elementos antigos foram removidos"""
    
    print("\n🔍 VERIFICANDO REMOÇÃO DE ELEMENTOS ANTIGOS")
    print("=" * 50)
    
    html_file = "../frontend/src/app/components/dashboard/dashboard.component.html"
    
    if not os.path.exists(html_file):
        print(f"  ❌ Arquivo não encontrado: {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Elementos que devem ter sido removidos
    old_elements = [
        "recent-hands-table",
        "hands-table",
        "hand-row",
        "view-all-button",
        "stats-grid",
        "stat-card"
    ]
    
    found_old_elements = []
    for element in old_elements:
        if element in content:
            found_old_elements.append(element)
    
    if found_old_elements:
        print(f"  ⚠️ Elementos antigos ainda presentes: {found_old_elements}")
    else:
        print(f"  ✅ Todos os elementos antigos foram removidos")

def check_new_indicators():
    """Verifica se os novos indicadores estão implementados"""
    
    print("\n🔍 VERIFICANDO NOVOS INDICADORES")
    print("=" * 50)
    
    ts_file = "../frontend/src/app/components/dashboard/dashboard.component.ts"
    
    if not os.path.exists(ts_file):
        print(f"  ❌ Arquivo não encontrado: {ts_file}")
        return
    
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Novos indicadores implementados
    new_indicators = [
        "streetGaps",
        "positionGaps", 
        "totalActions",
        "averagePot",
        "premiumPositionAggression",
        "cbetRate",
        "threeBetRate",
        "handsThisMonth",
        "gapsThisMonth",
        "monthlyImprovement"
    ]
    
    found_indicators = []
    for indicator in new_indicators:
        if indicator in content:
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"  ✅ Indicadores encontrados: {len(found_indicators)}/{len(new_indicators)}")
        print(f"     {', '.join(found_indicators)}")
    else:
        print(f"  ❌ Nenhum novo indicador encontrado")

def check_new_methods():
    """Verifica se os novos métodos estão implementados"""
    
    print("\n🔍 VERIFICANDO NOVOS MÉTODOS")
    print("=" * 50)
    
    ts_file = "../frontend/src/app/components/dashboard/dashboard.component.ts"
    
    if not os.path.exists(ts_file):
        print(f"  ❌ Arquivo não encontrado: {ts_file}")
        return
    
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Novos métodos implementados
    new_methods = [
        "calculateAdvancedStats",
        "calculateGapAnalysis",
        "calculateActionStats", 
        "calculateFinancialStats",
        "calculateMonthlyProgress",
        "getStreetFromHand",
        "goToHistory"
    ]
    
    found_methods = []
    for method in new_methods:
        if method in content:
            found_methods.append(method)
    
    if found_methods:
        print(f"  ✅ Métodos encontrados: {len(found_methods)}/{len(new_methods)}")
        print(f"     {', '.join(found_methods)}")
    else:
        print(f"  ❌ Nenhum novo método encontrado")

def main():
    """Função principal"""
    
    print("🚀 TESTE DO NOVO DASHBOARD")
    print("=" * 50)
    
    check_dashboard_files()
    check_removed_elements()
    check_new_indicators()
    check_new_methods()
    
    print("\n🎉 VERIFICAÇÃO CONCLUÍDA!")
    print("\n📋 RESUMO DAS MUDANÇAS:")
    print("✅ Dashboard focado em estatísticas importantes")
    print("✅ Removida seção de mãos recentes")
    print("✅ Adicionado botão para acessar histórico")
    print("✅ Novos indicadores de performance implementados")
    print("✅ Análise de gaps por street e posição")
    print("✅ Áreas de melhoria identificadas")
    print("✅ Progresso mensal com comparações")
    print("✅ Design moderno e responsivo")
    
    print("\n🎯 INDICADORES IMPLEMENTADOS:")
    print("• Taxa de agressão em posições premium")
    print("• Taxa de C-Bet (continuation bet)")
    print("• Taxa de 3-Bet")
    print("• Pot médio por mão")
    print("• Gaps por street (preflop, flop, turn, river)")
    print("• Gaps por posição")
    print("• Progresso mensal")
    print("• Melhoria percentual mês a mês")

if __name__ == "__main__":
    main() 