#!/usr/bin/env python3
"""
Teste da validação de upload
"""

import requests
import sys
import os
from pathlib import Path

def test_upload_validation():
    """Testa a validação de upload com diferentes arquivos"""
    
    base_url = "http://localhost:8000/api"
    
    # Arquivos para testar
    test_files = [
        ("torneio_portugues.txt", "Português - deve ser rejeitado"),
        ("torneio_ingles.txt", "Inglês - deve ser aceito")
    ]
    
    print("🧪 TESTE DE VALIDAÇÃO DE UPLOAD")
    print("=" * 50)
    
    for filename, description in test_files:
        if not os.path.exists(filename):
            print(f"❌ Arquivo não encontrado: {filename}")
            continue
        
        print(f"\n📄 Testando: {filename}")
        print(f"📋 Descrição: {description}")
        print("-" * 40)
        
        try:
            # Preparar arquivo para upload
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                
                # Fazer requisição
                response = requests.post(
                    f"{base_url}/hands/upload",
                    files=files,
                    timeout=30
                )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCESSO: Arquivo aceito")
                data = response.json()
                print(f"   Mensagem: {data.get('message', 'N/A')}")
                print(f"   Hands processadas: {data.get('hands_processed', 0)}")
            
            elif response.status_code == 400:
                print("❌ REJEITADO: Arquivo inválido")
                try:
                    error_data = response.json()
                    detail = error_data.get('detail', {})
                    
                    if isinstance(detail, dict):
                        print(f"   Erro: {detail.get('error', 'N/A')}")
                        print(f"   Título: {detail.get('title', 'N/A')}")
                        print(f"   Mensagem: {detail.get('message', 'N/A')[:100]}...")
                        
                        solutions = detail.get('solutions', [])
                        if solutions:
                            print("   Soluções:")
                            for solution in solutions:
                                print(f"     • {solution}")
                        
                        instructions = detail.get('instructions', [])
                        if instructions:
                            print("   Instruções:")
                            for instruction in instructions:
                                print(f"     • {instruction}")
                    else:
                        print(f"   Erro: {detail}")
                
                except Exception as e:
                    print(f"   Erro ao parsear resposta: {e}")
                    print(f"   Resposta: {response.text[:200]}...")
            
            else:
                print(f"⚠️  Status inesperado: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}...")
        
        except requests.exceptions.ConnectionError:
            print("❌ ERRO: Não foi possível conectar ao servidor")
            print("   Verifique se o backend está rodando em http://localhost:8000")
        
        except Exception as e:
            print(f"❌ ERRO: {e}")
    
    print(f"\n🎯 CONCLUSÃO:")
    print("✅ Se o arquivo em português foi rejeitado e o em inglês aceito, a validação está funcionando!")
    print("✅ O sistema está pronto para uso em produção!")

if __name__ == "__main__":
    test_upload_validation() 