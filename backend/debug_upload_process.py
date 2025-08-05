#!/usr/bin/env python3
"""
Debug do Processo de Upload
Analisa por que apenas 5 mãos estão sendo carregadas do torneio_ingles.txt
"""

import os
import re
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class DebugUploadProcess:
    def __init__(self):
        self.file_path = "torneio_ingles.txt"
        self.results = {
            "total_hands_found": 0,
            "hands_processed": 0,
            "hands_saved": 0,
            "errors": [],
            "debug_info": {}
        }
        
    def analyze_file_structure(self):
        """Analisa a estrutura do arquivo"""
        print("📁 ANALISANDO ESTRUTURA DO ARQUIVO")
        print("=" * 40)
        
        if not os.path.exists(self.file_path):
            print(f"❌ Arquivo {self.file_path} não encontrado!")
            return False
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Contar mãos no arquivo
        hand_matches = re.findall(r"PokerStars Hand #(\d+):", content)
        total_hands = len(hand_matches)
        
        print(f"📊 Total de mãos encontradas no arquivo: {total_hands}")
        print(f"📏 Tamanho do arquivo: {len(content)} caracteres")
        
        # Verificar se há problemas de codificação
        if content.count('\x00') > 0:
            print("⚠️ Arquivo contém caracteres nulos")
            
        # Verificar se há problemas de quebra de linha
        lines = content.split('\n')
        print(f"📄 Total de linhas: {len(lines)}")
        
        self.results["total_hands_found"] = total_hands
        self.results["debug_info"]["file_size"] = len(content)
        self.results["debug_info"]["total_lines"] = len(lines)
        
        return True
        
    def simulate_upload_parsing(self):
        """Simula o processo de parsing do upload"""
        print("\n🔍 SIMULANDO PROCESSO DE PARSING")
        print("-" * 35)
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Dividir em mãos
        hands = content.split("PokerStars Hand #")
        hands = [h for h in hands if h.strip()]  # Remover vazios
        
        print(f"📊 Mãos separadas: {len(hands)}")
        
        processed_hands = 0
        saved_hands = 0
        errors = []
        
        for i, hand_text in enumerate(hands[:10], 1):  # Analisar apenas as primeiras 10
            print(f"\n📋 Processando Mão {i}:")
            
            # Adicionar prefixo de volta
            full_hand = "PokerStars Hand #" + hand_text
            
            # Extrair hand ID
            hand_id_match = re.search(r"PokerStars Hand #(\d+):", full_hand)
            if not hand_id_match:
                print(f"  ❌ Hand ID não encontrado")
                errors.append(f"Mão {i}: Hand ID não encontrado")
                continue
                
            hand_id = hand_id_match.group(1)
            print(f"  🆔 Hand ID: {hand_id}")
            
            # Verificar se a mão tem estrutura básica
            if "Tournament #" not in full_hand:
                print(f"  ❌ Tournament ID não encontrado")
                errors.append(f"Mão {i}: Tournament ID não encontrado")
                continue
                
            if "Table '" not in full_hand:
                print(f"  ❌ Table name não encontrado")
                errors.append(f"Mão {i}: Table name não encontrado")
                continue
                
            # Verificar se tem ações
            action_count = len(re.findall(r"(\w+): (folds|calls|raises|bets|checks|all-in)", full_hand))
            print(f"  🎯 Ações encontradas: {action_count}")
            
            if action_count == 0:
                print(f"  ⚠️ Nenhuma ação encontrada")
                
            processed_hands += 1
            
            # Simular salvamento
            if len(full_hand) > 100:  # Mão tem tamanho mínimo
                saved_hands += 1
                print(f"  ✅ Mão válida para salvamento")
            else:
                print(f"  ❌ Mão muito pequena para salvamento")
                errors.append(f"Mão {i}: Tamanho insuficiente")
                
        self.results["hands_processed"] = processed_hands
        self.results["hands_saved"] = saved_hands
        self.results["errors"] = errors
        
        print(f"\n📊 RESUMO DO PARSING:")
        print(f"  Mãos processadas: {processed_hands}")
        print(f"  Mãos válidas para salvamento: {saved_hands}")
        print(f"  Erros encontrados: {len(errors)}")
        
    def check_database_hands(self):
        """Verifica mãos no banco de dados"""
        print("\n🗄️ VERIFICANDO MÃOS NO BANCO DE DADOS")
        print("-" * 40)
        
        try:
            engine = create_engine("sqlite:///gaphunter.db")
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Contar total de mãos
            result = session.execute(text("SELECT COUNT(*) FROM hands"))
            total_hands = result.fetchone()[0]
            print(f"📊 Total de mãos no banco: {total_hands}")
            
            # Verificar mãos por usuário
            result = session.execute(text("""
                SELECT user_id, COUNT(*) as hand_count 
                FROM hands 
                GROUP BY user_id
            """))
            users_hands = [row for row in result]
            
            print(f"\n📋 MÃOS POR USUÁRIO:")
            for user_id, hand_count in users_hands:
                print(f"  • User ID {user_id}: {hand_count} mãos")
                
            # Verificar últimas mãos carregadas
            if total_hands > 0:
                print(f"\n📋 ÚLTIMAS 10 MÃOS CARREGADAS:")
                result = session.execute(text("""
                    SELECT hand_id, hero_name, hero_cards, created_at 
                    FROM hands 
                    ORDER BY id DESC 
                    LIMIT 10
                """))
                
                hands = [row for row in result]
                for hand in hands:
                    print(f"  • Hand #{hand[0]} - {hand[1]} - {hand[2]} - {hand[3]}")
                    
            session.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
            
    def check_upload_logs(self):
        """Verifica logs de upload se existirem"""
        print("\n📋 VERIFICANDO LOGS DE UPLOAD")
        print("-" * 30)
        
        log_files = [f for f in os.listdir('.') if 'upload' in f.lower() and f.endswith('.json')]
        
        if log_files:
            print(f"📄 Logs encontrados: {log_files}")
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                        
                    print(f"\n📊 {log_file}:")
                    if "hands_processed" in log_data:
                        print(f"  • Mãos processadas: {log_data['hands_processed']}")
                    if "hands_saved" in log_data:
                        print(f"  • Mãos salvas: {log_data['hands_saved']}")
                    if "errors" in log_data:
                        print(f"  • Erros: {len(log_data['errors'])}")
                        
                except Exception as e:
                    print(f"  ❌ Erro ao ler {log_file}: {e}")
        else:
            print("ℹ️ Nenhum log de upload encontrado")
            
    def analyze_upload_errors(self):
        """Analisa possíveis causas dos erros de upload"""
        print("\n🔍 ANÁLISE DE POSSÍVEIS CAUSAS")
        print("-" * 35)
        
        causes = [
            "1. **Limite de processamento**: O sistema pode ter um limite de 5 mãos por upload",
            "2. **Timeout**: O processo pode estar sendo interrompido por timeout",
            "3. **Erro de parsing**: Algumas mãos podem ter formato inválido",
            "4. **Problema de memória**: O sistema pode estar esgotando memória",
            "5. **Erro de banco de dados**: Problemas de conexão ou constraints",
            "6. **Problema de codificação**: Caracteres especiais no arquivo",
            "7. **Estrutura de mão inválida**: Mãos com formato não reconhecido"
        ]
        
        for cause in causes:
            print(f"  {cause}")
            
    def generate_recommendations(self):
        """Gera recomendações para corrigir o problema"""
        print("\n💡 RECOMENDAÇÕES PARA CORREÇÃO")
        print("-" * 35)
        
        recommendations = [
            "1. **Verificar logs do backend** para identificar erros específicos",
            "2. **Aumentar timeout** do processo de upload",
            "3. **Verificar limites** de processamento no código",
            "4. **Testar com arquivo menor** para isolar o problema",
            "5. **Verificar codificação** do arquivo (UTF-8)",
            "6. **Analisar estrutura** das mãos que falharam",
            "7. **Verificar constraints** do banco de dados",
            "8. **Implementar retry logic** para mãos que falharam"
        ]
        
        for rec in recommendations:
            print(f"  {rec}")
            
    def save_debug_report(self):
        """Salva relatório de debug"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_debug_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Relatório de debug salvo em: {filename}")
        
    def run_debug_analysis(self):
        """Executa análise completa de debug"""
        print("🚀 INICIANDO ANÁLISE DE DEBUG - UPLOAD TORNEIO_INGLES.TXT")
        print("=" * 65)
        
        # 1. Analisar estrutura do arquivo
        if not self.analyze_file_structure():
            return False
            
        # 2. Simular processo de parsing
        self.simulate_upload_parsing()
        
        # 3. Verificar mãos no banco
        self.check_database_hands()
        
        # 4. Verificar logs de upload
        self.check_upload_logs()
        
        # 5. Analisar possíveis causas
        self.analyze_upload_errors()
        
        # 6. Gerar recomendações
        self.generate_recommendations()
        
        # 7. Salvar relatório
        self.save_debug_report()
        
        print("\n✅ ANÁLISE DE DEBUG CONCLUÍDA!")
        return True

def main():
    debugger = DebugUploadProcess()
    success = debugger.run_debug_analysis()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Analise o relatório de debug")
        print("2. Implemente as correções sugeridas")
        print("3. Teste o upload novamente")
    else:
        print("\n❌ Análise falhou. Verifique os erros acima.")
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    import sys
    main() 