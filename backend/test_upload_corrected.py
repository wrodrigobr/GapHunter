#!/usr/bin/env python3
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
