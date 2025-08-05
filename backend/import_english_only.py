#!/usr/bin/env python3
"""
Importador de Hand History - Exige formato em inglês
"""

import os
import sys
from pathlib import Path
from hand_history_validator import HandHistoryValidator

class EnglishOnlyImporter:
    """Importador que exige hand history em inglês"""
    
    def __init__(self):
        self.validator = HandHistoryValidator()
    
    def validate_file(self, file_path: str) -> tuple[bool, str, str]:
        """
        Valida um arquivo de hand history
        Retorna: (is_valid, language, error_message)
        """
        
        try:
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                return False, "unknown", f"Arquivo não encontrado: {file_path}"
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validar conteúdo
            return self.validator.validate_hand_history(content)
            
        except UnicodeDecodeError:
            return False, "unknown", "Erro de codificação: arquivo não está em UTF-8"
        except Exception as e:
            return False, "unknown", f"Erro ao ler arquivo: {str(e)}"
    
    def validate_directory(self, directory_path: str) -> dict:
        """
        Valida todos os arquivos .txt em um diretório
        Retorna: dicionário com resultados
        """
        
        results = {
            'valid_files': [],
            'invalid_files': [],
            'total_files': 0,
            'valid_count': 0,
            'invalid_count': 0
        }
        
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                return {'error': f'Diretório não encontrado: {directory_path}'}
            
            # Buscar arquivos .txt
            txt_files = list(directory.glob('*.txt'))
            results['total_files'] = len(txt_files)
            
            print(f"🔍 Encontrados {len(txt_files)} arquivos .txt")
            
            for file_path in txt_files:
                print(f"\n📄 Validando: {file_path.name}")
                
                is_valid, language, message = self.validate_file(str(file_path))
                
                if is_valid:
                    results['valid_files'].append({
                        'file': str(file_path),
                        'language': language,
                        'message': message
                    })
                    results['valid_count'] += 1
                    print(f"✅ Válido ({language})")
                else:
                    results['invalid_files'].append({
                        'file': str(file_path),
                        'language': language,
                        'message': message
                    })
                    results['invalid_count'] += 1
                    print(f"❌ Inválido ({language})")
                    print(f"   {message[:100]}...")
            
            return results
            
        except Exception as e:
            return {'error': f'Erro ao processar diretório: {str(e)}'}
    
    def show_validation_summary(self, results: dict):
        """Mostra resumo da validação"""
        
        if 'error' in results:
            print(f"❌ {results['error']}")
            return
        
        print(f"\n📊 RESUMO DA VALIDAÇÃO")
        print("=" * 50)
        print(f"📁 Total de arquivos: {results['total_files']}")
        print(f"✅ Arquivos válidos: {results['valid_count']}")
        print(f"❌ Arquivos inválidos: {results['invalid_count']}")
        
        if results['valid_count'] > 0:
            print(f"\n✅ ARQUIVOS VÁLIDOS:")
            for file_info in results['valid_files']:
                print(f"   - {Path(file_info['file']).name}")
        
        if results['invalid_count'] > 0:
            print(f"\n❌ ARQUIVOS INVÁLIDOS:")
            for file_info in results['invalid_files']:
                print(f"   - {Path(file_info['file']).name} ({file_info['language']})")
        
        # Mostrar formatos suportados
        print(f"\n📋 FORMATOS SUPORTADOS:")
        print(self.validator.get_supported_formats())

def main():
    """Função principal"""
    
    print("🔍 VALIDADOR DE HAND HISTORY - INGLÊS OBRIGATÓRIO")
    print("=" * 60)
    
    importer = EnglishOnlyImporter()
    
    if len(sys.argv) < 2:
        print("❌ Uso: python import_english_only.py <arquivo_ou_diretorio>")
        print("\n📋 Exemplos:")
        print("   python import_english_only.py hand_history.txt")
        print("   python import_english_only.py ./hand_histories/")
        return
    
    target_path = sys.argv[1]
    
    if os.path.isfile(target_path):
        # Validar arquivo único
        print(f"📄 Validando arquivo: {target_path}")
        is_valid, language, message = importer.validate_file(target_path)
        
        if is_valid:
            print(f"✅ ARQUIVO VÁLIDO!")
            print(f"🌍 Idioma: {language}")
            print(f"💬 {message}")
        else:
            print(f"❌ ARQUIVO INVÁLIDO!")
            print(f"🌍 Idioma: {language}")
            print(f"💬 {message}")
    
    elif os.path.isdir(target_path):
        # Validar diretório
        print(f"📁 Validando diretório: {target_path}")
        results = importer.validate_directory(target_path)
        importer.show_validation_summary(results)
    
    else:
        print(f"❌ Caminho não encontrado: {target_path}")

if __name__ == "__main__":
    main() 