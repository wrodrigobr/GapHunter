#!/usr/bin/env python3
"""
Serviço de validação de hand history
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para importar o validador
backend_root = Path(__file__).parent.parent.parent
sys.path.append(str(backend_root))

from hand_history_validator import HandHistoryValidator

class ValidationService:
    """Serviço para validar hand history"""
    
    def __init__(self):
        self.validator = HandHistoryValidator()
    
    async def validate_hand_history_file(self, content: str, filename: str) -> dict:
        """
        Valida o conteúdo de um arquivo de hand history
        Retorna: dict com resultado da validação
        """
        
        try:
            # Validar o conteúdo
            is_valid, language, message = self.validator.validate_hand_history(content)
            
            return {
                "is_valid": is_valid,
                "language": language,
                "message": message,
                "filename": filename,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "language": "unknown",
                "message": f"Erro durante validação: {str(e)}",
                "filename": filename,
                "content_length": len(content) if content else 0
            }
    
    def get_validation_error_response(self, validation_result: dict) -> dict:
        """
        Gera resposta de erro formatada para o frontend
        """
        
        if validation_result["language"] == "portuguese":
            return {
                "error": "HAND_HISTORY_PORTUGUESE",
                "title": "Arquivo em Português Detectado",
                "message": validation_result["message"],
                "solutions": [
                    "Configure o PokerStars para exportar hand history em inglês",
                    "Use um tradutor online para converter português → inglês",
                    "Aguarde a próxima versão que suportará múltiplos idiomas"
                ],
                "instructions": [
                    "Abra o PokerStars",
                    "Vá em Configurações > Interface",
                    "Altere o idioma para 'English'",
                    "Reexporte os hand histories"
                ]
            }
        
        elif validation_result["language"] == "spanish":
            return {
                "error": "HAND_HISTORY_SPANISH",
                "title": "Arquivo em Espanhol Detectado",
                "message": validation_result["message"],
                "solutions": [
                    "Configure o PokerStars para exportar hand history em inglês",
                    "Use um tradutor online para converter espanhol → inglês",
                    "Aguarde a próxima versão que suportará múltiplos idiomas"
                ]
            }
        
        else:
            return {
                "error": "HAND_HISTORY_INVALID",
                "title": "Formato Inválido",
                "message": validation_result["message"],
                "solutions": [
                    "Verifique se o arquivo contém hand history do PokerStars",
                    "Confirme que o formato está em inglês",
                    "Verifique se o arquivo não está corrompido"
                ]
            }

# Instância global do serviço
validation_service = ValidationService() 