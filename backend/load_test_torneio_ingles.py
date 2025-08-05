#!/usr/bin/env python3
"""
Teste de Carga - torneio_ingles.txt
Análise de performance e identificação de problemas
"""

import os
import sys
import time
import psutil
import json
from datetime import datetime
import re

class LoadTestTorneioIngles:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.results = {
            "file_info": {},
            "performance_analysis": {},
            "issues": [],
            "recommendations": []
        }
        
    def get_file_info(self):
        """Obtém informações detalhadas do arquivo"""
        print("📁 ANALISANDO ARQUIVO TORNEIO_INGLES.TXT")
        print("=" * 50)
        
        if not os.path.exists(self.file_path):
            print(f"❌ Arquivo {self.file_path} não encontrado!")
            return False
            
        file_size = os.path.getsize(self.file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            total_lines = len(lines)
            
        print(f"✅ Arquivo encontrado: {self.file_path}")
        print(f"📏 Tamanho: {file_size_mb:.2f} MB")
        print(f"📄 Linhas: {total_lines:,}")
        
        # Análise detalhada do conteúdo
        hand_count = 0
        tournament_count = 0
        player_count = 0
        action_count = 0
        players = set()
        
        for line in lines:
            line = line.strip()
            
            # Contar mãos
            if line.startswith("PokerStars Hand #"):
                hand_count += 1
                
            # Contar torneios
            if "Tournament #" in line:
                tournament_count += 1
                
            # Contar jogadores
            if "Seat " in line and ":" in line:
                player_match = re.search(r'Seat \d+: (.+?) \(', line)
                if player_match:
                    players.add(player_match.group(1))
                    
            # Contar ações
            if any(action in line for action in ['folds', 'calls', 'raises', 'bets', 'checks', 'all-in']):
                action_count += 1
                
        player_count = len(players)
        
        print(f"🃏 Mãos encontradas: {hand_count:,}")
        print(f"🏆 Torneios encontrados: {tournament_count:,}")
        print(f"👥 Jogadores únicos: {player_count:,}")
        print(f"🎯 Ações encontradas: {action_count:,}")
        
        # Calcular métricas
        avg_hands_per_tournament = hand_count / max(tournament_count, 1)
        avg_actions_per_hand = action_count / max(hand_count, 1)
        
        print(f"📊 Média de mãos por torneio: {avg_hands_per_tournament:.1f}")
        print(f"📊 Média de ações por mão: {avg_actions_per_hand:.1f}")
        
        self.results["file_info"] = {
            "file_path": self.file_path,
            "size_bytes": file_size,
            "size_mb": file_size_mb,
            "total_lines": total_lines,
            "hand_count": hand_count,
            "tournament_count": tournament_count,
            "player_count": player_count,
            "action_count": action_count,
            "avg_hands_per_tournament": avg_hands_per_tournament,
            "avg_actions_per_hand": avg_actions_per_hand
        }
        
        return True
        
    def simulate_parsing_performance(self):
        """Simula performance do parsing"""
        print("\n⚡ SIMULANDO PERFORMANCE DO PARSING")
        print("-" * 40)
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Simular parsing linha por linha
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        parsed_hands = []
        current_hand = []
        hand_count = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("PokerStars Hand #"):
                if current_hand:
                    parsed_hands.append(current_hand)
                    hand_count += 1
                current_hand = [line]
            elif line and current_hand:
                current_hand.append(line)
                
        # Adicionar última mão
        if current_hand:
            parsed_hands.append(current_hand)
            hand_count += 1
            
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        duration = end_time - start_time
        memory_used = end_memory - start_memory
        
        print(f"⏱️ Tempo de parsing: {duration:.2f}s")
        print(f"💾 Memória usada: {memory_used:.2f} MB")
        print(f"📊 Mãos parseadas: {hand_count}")
        print(f"⚡ Velocidade: {hand_count/duration:.1f} mãos/segundo")
        
        self.results["performance_analysis"] = {
            "parsing_duration": duration,
            "memory_used_mb": memory_used,
            "hands_parsed": hand_count,
            "speed_hands_per_second": hand_count/duration if duration > 0 else 0
        }
        
    def identify_performance_issues(self):
        """Identifica problemas de performance"""
        print("\n🔍 IDENTIFICANDO PROBLEMAS DE PERFORMANCE")
        print("-" * 45)
        
        issues = []
        file_info = self.results["file_info"]
        perf_info = self.results["performance_analysis"]
        
        # Verificar tamanho do arquivo
        if file_info["size_mb"] > 1:
            issues.append("📁 Arquivo grande (>1MB) - pode causar timeout no upload")
            
        # Verificar número de mãos
        if file_info["hand_count"] > 100:
            issues.append("🃏 Muitas mãos (>100) - processamento pode ser lento")
            
        # Verificar tempo de parsing
        if perf_info["parsing_duration"] > 10:
            issues.append("⏱️ Parsing lento (>10s) - otimização necessária")
            
        # Verificar uso de memória
        if perf_info["memory_used_mb"] > 100:
            issues.append("💾 Uso de memória alto (>100MB) - otimização necessária")
            
        # Verificar velocidade de parsing
        if perf_info["speed_hands_per_second"] < 10:
            issues.append("🐌 Velocidade de parsing baixa (<10 mãos/s) - otimização necessária")
            
        if issues:
            print("⚠️ PROBLEMAS IDENTIFICADOS:")
            for issue in issues:
                print(f"  • {issue}")
                self.results["issues"].append(issue)
        else:
            print("✅ Nenhum problema crítico identificado")
            
    def generate_optimization_recommendations(self):
        """Gera recomendações de otimização"""
        print("\n💡 RECOMENDAÇÕES DE OTIMIZAÇÃO")
        print("=" * 35)
        
        recommendations = []
        file_info = self.results["file_info"]
        perf_info = self.results["performance_analysis"]
        
        # Recomendações baseadas no tamanho
        if file_info["size_mb"] > 0.5:
            recommendations.append("📦 Implementar upload em chunks para arquivos grandes")
            recommendations.append("🔄 Adicionar barra de progresso para feedback visual")
            
        # Recomendações baseadas no número de mãos
        if file_info["hand_count"] > 50:
            recommendations.append("⚡ Processar mãos em lotes para melhor performance")
            recommendations.append("💾 Implementar cache para dados processados")
            
        # Recomendações baseadas na performance
        if perf_info["parsing_duration"] > 5:
            recommendations.append("🔧 Otimizar parser de hand history")
            recommendations.append("📊 Implementar parsing paralelo")
            
        # Recomendações gerais
        recommendations.append("🛡️ Adicionar validação de dados antes do processamento")
        recommendations.append("📈 Implementar métricas de performance em tempo real")
        recommendations.append("🎯 Otimizar regex patterns para parsing mais rápido")
        recommendations.append("💡 Implementar lazy loading para mãos grandes")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
            
        self.results["recommendations"] = recommendations
        
    def analyze_memory_usage(self):
        """Analisa uso de memória detalhado"""
        print("\n💾 ANÁLISE DE USO DE MEMÓRIA")
        print("-" * 30)
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        print(f"📊 Memória RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
        print(f"📊 Memória VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
        print(f"📊 Memória disponível: {psutil.virtual_memory().available / 1024 / 1024:.2f} MB")
        
        # Verificar se há problemas de memória
        if memory_info.rss > 200 * 1024 * 1024:  # 200MB
            self.results["issues"].append("💾 Uso de memória muito alto (>200MB)")
            
    def save_results(self):
        """Salva resultados do teste"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Resultados salvos em: {filename}")
        
    def run_full_test(self):
        """Executa teste completo"""
        print("🚀 INICIANDO TESTE DE CARGA - TORNEIO_INGLES.TXT")
        print("=" * 60)
        
        # 1. Análise do arquivo
        if not self.get_file_info():
            return False
            
        # 2. Simulação de performance
        self.simulate_parsing_performance()
        
        # 3. Análise de memória
        self.analyze_memory_usage()
        
        # 4. Identificação de problemas
        self.identify_performance_issues()
        
        # 5. Recomendações
        self.generate_optimization_recommendations()
        
        # 6. Salvar resultados
        self.save_results()
        
        print("\n✅ TESTE DE CARGA CONCLUÍDO!")
        return True

def main():
    load_test = LoadTestTorneioIngles()
    success = load_test.run_full_test()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Analise os resultados salvos")
        print("2. Implemente as recomendações de otimização")
        print("3. Execute o teste novamente para verificar melhorias")
    else:
        print("\n❌ Teste falhou. Verifique os erros acima.")
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 