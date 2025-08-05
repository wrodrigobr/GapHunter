#!/usr/bin/env python3
"""
Comparação de Resultados - Teste de Carga
Compara resultados antes e depois das otimizações
"""

import os
import json
from datetime import datetime

def compare_load_test_results():
    """Compara resultados dos testes de carga"""
    print("📊 COMPARAÇÃO DE RESULTADOS - TESTE DE CARGA")
    print("=" * 55)
    
    # Encontrar arquivos de resultados
    result_files = [f for f in os.listdir('.') if f.startswith('load_test_results_')]
    if len(result_files) < 2:
        print("❌ Necessário pelo menos 2 arquivos de resultados para comparação")
        return
        
    # Ordenar por timestamp (mais antigo primeiro)
    result_files.sort()
    
    # Carregar resultados
    before_results = None
    after_results = None
    
    for i, filename in enumerate(result_files):
        with open(filename, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
        if i == 0:
            before_results = results
            print(f"📋 ANTES: {filename}")
        elif i == len(result_files) - 1:
            after_results = results
            print(f"📋 DEPOIS: {filename}")
            
    if not before_results or not after_results:
        print("❌ Não foi possível carregar os resultados")
        return
        
    # Comparar métricas
    print("\n📈 COMPARAÇÃO DE MÉTRICAS")
    print("-" * 30)
    
    before_perf = before_results.get("performance_analysis", {})
    after_perf = after_results.get("performance_analysis", {})
    
    before_duration = before_perf.get("parsing_duration", 0)
    after_duration = after_perf.get("parsing_duration", 0)
    duration_improvement = ((before_duration - after_duration) / before_duration * 100) if before_duration > 0 else 0
    
    before_memory = before_perf.get("memory_used_mb", 0)
    after_memory = after_perf.get("memory_used_mb", 0)
    memory_improvement = ((before_memory - after_memory) / before_memory * 100) if before_memory > 0 else 0
    
    before_speed = before_perf.get("speed_hands_per_second", 0)
    after_speed = after_perf.get("speed_hands_per_second", 0)
    speed_improvement = ((after_speed - before_speed) / before_speed * 100) if before_speed > 0 else 0
    
    print(f"⏱️ Tempo de parsing:")
    print(f"   ANTES: {before_duration:.3f}s")
    print(f"   DEPOIS: {after_duration:.3f}s")
    print(f"   MELHORIA: {duration_improvement:+.1f}%")
    
    print(f"\n💾 Memória usada:")
    print(f"   ANTES: {before_memory:.2f} MB")
    print(f"   DEPOIS: {after_memory:.2f} MB")
    print(f"   MELHORIA: {memory_improvement:+.1f}%")
    
    print(f"\n⚡ Velocidade:")
    print(f"   ANTES: {before_speed:.1f} mãos/s")
    print(f"   DEPOIS: {after_speed:.1f} mãos/s")
    print(f"   MELHORIA: {speed_improvement:+.1f}%")
    
    # Comparar problemas identificados
    print("\n🔍 PROBLEMAS IDENTIFICADOS")
    print("-" * 30)
    
    before_issues = before_results.get("issues", [])
    after_issues = after_results.get("issues", [])
    
    print(f"ANTES: {len(before_issues)} problemas")
    for issue in before_issues:
        print(f"  • {issue}")
        
    print(f"\nDEPOIS: {len(after_issues)} problemas")
    for issue in after_issues:
        print(f"  • {issue}")
        
    # Análise de melhoria
    print("\n📊 ANÁLISE DE MELHORIA")
    print("-" * 25)
    
    improvements = []
    
    if duration_improvement > 0:
        improvements.append(f"✅ Tempo de parsing melhorou em {duration_improvement:.1f}%")
    else:
        improvements.append(f"❌ Tempo de parsing piorou em {abs(duration_improvement):.1f}%")
        
    if memory_improvement > 0:
        improvements.append(f"✅ Uso de memória melhorou em {memory_improvement:.1f}%")
    else:
        improvements.append(f"❌ Uso de memória piorou em {abs(memory_improvement):.1f}%")
        
    if speed_improvement > 0:
        improvements.append(f"✅ Velocidade melhorou em {speed_improvement:.1f}%")
    else:
        improvements.append(f"❌ Velocidade piorou em {abs(speed_improvement):.1f}%")
        
    if len(after_issues) < len(before_issues):
        improvements.append(f"✅ Redução de {len(before_issues) - len(after_issues)} problemas")
    elif len(after_issues) > len(before_issues):
        improvements.append(f"❌ Aumento de {len(after_issues) - len(before_issues)} problemas")
    else:
        improvements.append("➖ Mesmo número de problemas")
        
    for improvement in improvements:
        print(improvement)
        
    # Salvar comparação
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "before_file": result_files[0],
        "after_file": result_files[-1],
        "metrics": {
            "duration_before": before_duration,
            "duration_after": after_duration,
            "duration_improvement": duration_improvement,
            "memory_before": before_memory,
            "memory_after": after_memory,
            "memory_improvement": memory_improvement,
            "speed_before": before_speed,
            "speed_after": after_speed,
            "speed_improvement": speed_improvement
        },
        "issues": {
            "before_count": len(before_issues),
            "after_count": len(after_issues),
            "before_issues": before_issues,
            "after_issues": after_issues
        },
        "improvements": improvements
    }
    
    comparison_filename = f"load_test_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(comparison_filename, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Comparação salva em: {comparison_filename}")
    
    # Resumo final
    print("\n🎯 RESUMO FINAL")
    print("=" * 15)
    
    positive_improvements = sum(1 for imp in improvements if imp.startswith("✅"))
    total_improvements = len(improvements)
    
    if positive_improvements > total_improvements / 2:
        print("✅ OTIMIZAÇÕES EFETIVAS!")
        print("As melhorias implementadas tiveram impacto positivo na performance.")
    elif positive_improvements > 0:
        print("⚠️ MELHORIAS PARCIAIS")
        print("Algumas otimizações foram efetivas, mas há espaço para mais melhorias.")
    else:
        print("❌ OTIMIZAÇÕES INEFETIVAS")
        print("As otimizações não tiveram o impacto esperado. Revisão necessária.")

if __name__ == "__main__":
    compare_load_test_results() 