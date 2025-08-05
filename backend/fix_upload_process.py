#!/usr/bin/env python3
"""
Corrigir Processo de Upload
Remove o limite de commit a cada 5 mãos e melhora o tratamento de erros
"""

import os
import re

def fix_upload_process():
    """Corrige o processo de upload"""
    print("🔧 CORRIGINDO PROCESSO DE UPLOAD")
    print("=" * 35)
    
    file_path = "app/routers/upload_progress.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo {file_path} não encontrado!")
        return False
        
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"📄 Arquivo lido: {len(content)} caracteres")
    
    # Encontrar o problema
    problematic_code = """                # Commit a cada 5 mãos para debug
                if (i + 1) % 5 == 0:
                    db.commit()
                    upload_progress[upload_id]["message"] = f"Salvando progresso... ({i+1}/{total_hands})"
                    print(f"💾 Commit realizado: {i+1} mãos")"""
    
    fixed_code = """                # Commit a cada 10 mãos para melhor performance
                if (i + 1) % 10 == 0:
                    try:
                        db.commit()
                        upload_progress[upload_id]["message"] = f"Salvando progresso... ({i+1}/{total_hands})"
                        print(f"💾 Commit realizado: {i+1} mãos")
                    except Exception as commit_error:
                        print(f"⚠️ Erro no commit: {commit_error}")
                        db.rollback()"""
    
    if problematic_code in content:
        print("✅ Problema encontrado - removendo limite de 5 mãos")
        
        # Substituir o código problemático
        new_content = content.replace(problematic_code, fixed_code)
        
        # Adicionar melhor tratamento de erros
        error_handling = """            except Exception as e:
                error_msg = f"Erro na mão {i+1}: {str(e)}"
                upload_progress[upload_id]["errors"].append(error_msg)
                print(f"❌ {error_msg}")
                # Continuar processamento em vez de parar
                continue"""
        
        # Verificar se já existe tratamento de erro melhorado
        if "continue" not in content:
            old_error_handling = """            except Exception as e:
                error_msg = f"Erro na mão {i+1}: {str(e)}"
                upload_progress[upload_id]["errors"].append(error_msg)
                print(f"❌ {error_msg})"""
            
            if old_error_handling in new_content:
                new_content = new_content.replace(old_error_handling, error_handling)
                print("✅ Melhorado tratamento de erros")
        
        # Salvar backup
        backup_path = f"{file_path}.backup_{int(os.path.getmtime(file_path))}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Backup salvo em: {backup_path}")
        
        # Salvar arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Arquivo corrigido: {file_path}")
        
        return True
    else:
        print("ℹ️ Problema não encontrado no arquivo")
        return False

def create_upload_test_script():
    """Cria script para testar o upload corrigido"""
    print("\n🧪 CRIANDO SCRIPT DE TESTE DE UPLOAD")
    print("-" * 35)
    
    test_script = '''#!/usr/bin/env python3
"""
Teste de Upload Corrigido
Testa o upload do arquivo torneio_ingles.txt após as correções
"""

import requests
import time
import json

def test_upload():
    """Testa o upload corrigido"""
    print("🚀 TESTANDO UPLOAD CORRIGIDO")
    print("=" * 35)
    
    # URL do endpoint
    url = "http://localhost:8000/api/upload/upload-async"
    
    # Arquivo para upload
    file_path = "torneio_ingles.txt"
    
    try:
        # Fazer upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/plain')}
            response = requests.post(url, files=files, timeout=300)
            
        if response.status_code == 200:
            data = response.json()
            upload_id = data.get('upload_id')
            print(f"✅ Upload iniciado: {upload_id}")
            
            # Monitorar progresso
            progress_url = f"http://localhost:8000/api/upload/upload-progress/{upload_id}"
            
            while True:
                progress_response = requests.get(progress_url)
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    
                    status = progress_data.get('status')
                    progress = progress_data.get('progress', 0)
                    message = progress_data.get('message', '')
                    
                    print(f"📊 Progresso: {progress}% - {message}")
                    
                    if status == 'completed':
                        result = progress_data.get('result', {})
                        hands_processed = result.get('hands_processed', 0)
                        total_found = result.get('total_found', 0)
                        
                        print(f"✅ Upload concluído!")
                        print(f"📊 Mãos processadas: {hands_processed}")
                        print(f"📊 Total encontrado: {total_found}")
                        break
                    elif status == 'error':
                        errors = progress_data.get('errors', [])
                        print(f"❌ Upload falhou: {errors}")
                        break
                        
                time.sleep(2)
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_upload()
'''
    
    with open("test_upload_corrected.py", "w", encoding='utf-8') as f:
        f.write(test_script)
        
    print("✅ Script de teste criado: test_upload_corrected.py")

def main():
    """Executa correção do processo de upload"""
    print("🔧 INICIANDO CORREÇÃO DO PROCESSO DE UPLOAD")
    print("=" * 50)
    
    # 1. Corrigir o arquivo de upload
    if fix_upload_process():
        print("✅ Correção aplicada com sucesso")
    else:
        print("❌ Falha na correção")
        return False
        
    # 2. Criar script de teste
    create_upload_test_script()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Reinicie o servidor backend")
    print("2. Execute o script de teste: python test_upload_corrected.py")
    print("3. Verifique se mais mãos são carregadas")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 