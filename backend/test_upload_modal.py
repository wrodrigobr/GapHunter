#!/usr/bin/env python3
"""
Teste do Modal de Upload
Verifica se o modal de progresso está funcionando corretamente
"""

import requests
import time
import json

def login_and_get_token():
    """Faz login e retorna token de autenticação"""
    print("\n🔐 FAZENDO LOGIN")
    print("-" * 20)
    
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "username": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(login_url, data=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login realizado com sucesso")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def test_upload_modal(token):
    """Testa o modal de upload"""
    print("\n🧪 TESTE DO MODAL DE UPLOAD")
    print("=" * 40)
    
    # URL do endpoint
    url = "http://localhost:8000/api/upload/upload-async"
    
    # Arquivo pequeno para teste
    file_path = "20_hands_extracted.txt"
    
    # Headers com autenticação
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        print(f"📤 Fazendo upload do arquivo: {file_path}")
        
        # Fazer upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/plain')}
            response = requests.post(url, files=files, headers=headers, timeout=30)
            
        if response.status_code == 200:
            data = response.json()
            upload_id = data.get('upload_id')
            print(f"✅ Upload iniciado: {upload_id}")
            
            # Monitorar progresso
            progress_url = f"http://localhost:8000/api/upload/upload-progress/{upload_id}"
            
            print(f"\n📊 MONITORANDO PROGRESSO:")
            print("-" * 30)
            
            while True:
                progress_response = requests.get(progress_url)
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    
                    status = progress_data.get('status')
                    progress = progress_data.get('progress', 0)
                    message = progress_data.get('message', '')
                    processed_hands = progress_data.get('processed_hands', 0)
                    total_hands = progress_data.get('total_hands', 0)
                    
                    print(f"📈 Status: {status} | Progresso: {progress}% | Mãos: {processed_hands}/{total_hands}")
                    print(f"💬 Mensagem: {message}")
                    
                    if status == 'completed':
                        result = progress_data.get('result', {})
                        hands_processed = result.get('hands_processed', 0)
                        total_found = result.get('total_found', 0)
                        
                        print(f"\n✅ Upload concluído!")
                        print(f"📊 Mãos processadas: {hands_processed}")
                        print(f"📊 Total encontrado: {total_found}")
                        break
                    elif status == 'error':
                        errors = progress_data.get('errors', [])
                        print(f"❌ Upload falhou: {errors}")
                        break
                        
                time.sleep(1)
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_sse_stream():
    """Testa o stream SSE"""
    print("\n🌊 TESTE DO STREAM SSE")
    print("=" * 25)
    
    # Simular um upload_id
    upload_id = "test-upload-123"
    
    try:
        # Testar endpoint SSE
        sse_url = f"http://localhost:8000/api/upload/upload-stream/{upload_id}"
        print(f"🔗 Testando SSE: {sse_url}")
        
        response = requests.get(sse_url, timeout=5)
        print(f"📊 Status SSE: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro no teste SSE: {e}")

def check_backend_status():
    """Verifica status do backend"""
    print("\n🔍 VERIFICANDO STATUS DO BACKEND")
    print("-" * 35)
    
    try:
        # Testar health endpoint
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend está funcionando")
            print(f"📊 Resposta: {response.json()}")
        else:
            print(f"❌ Backend com problema: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Backend não está acessível: {e}")

def main():
    """Função principal"""
    print("🔧 TESTE COMPLETO DO MODAL DE UPLOAD")
    print("=" * 50)
    
    # 1. Verificar status do backend
    check_backend_status()
    
    # 2. Fazer login e obter token
    token = login_and_get_token()
    
    # 3. Testar stream SSE
    test_sse_stream()
    
    # 4. Testar upload completo (se tiver token)
    if token:
        test_upload_modal(token)
    else:
        print("\n❌ Não foi possível obter token de autenticação")
        print("💡 Crie um usuário de teste primeiro")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique se o modal aparece no frontend")
    print("2. Teste com arquivo maior para ver progresso")
    print("3. Verifique se o modal fecha automaticamente")

if __name__ == "__main__":
    main() 