#!/usr/bin/env python3
"""
Script para verificar o status do token do YouTube
Execute periodicamente para verificar se o token ainda está válido
"""

import os
import sys
import json
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_token_file():
    """Verifica se o arquivo token.json existe e é válido"""
    token_path = 'config/token.json'
    
    print("=" * 70)
    print("VERIFICAÇÃO DE STATUS DO TOKEN DO YOUTUBE")
    print("=" * 70)
    print()
    
    # Verificar existência
    if not os.path.exists(token_path):
        print("✗ Token não encontrado!")
        print(f"  Arquivo esperado: {token_path}")
        print()
        print("Para gerar um novo token:")
        print("  python config/generate_youtube_token.py")
        return False
    
    print(f"✓ Arquivo de token encontrado: {token_path}")
    
    # Verificar se é JSON válido
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        print("✓ Token é um JSON válido")
    except json.JSONDecodeError:
        print("✗ Token não é um JSON válido (arquivo corrompido)")
        print()
        print("Solução: Regenerar o token")
        print("  python config/generate_youtube_token.py")
        return False
    
    # Verificar campos obrigatórios
    required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
    missing_fields = [field for field in required_fields if field not in token_data]
    
    if missing_fields:
        print(f"✗ Token incompleto. Campos faltando: {', '.join(missing_fields)}")
        print()
        print("Solução: Regenerar o token")
        print("  python config/generate_youtube_token.py")
        return False
    
    print("✓ Token possui todos os campos necessários")
    
    # Verificar refresh_token
    if not token_data.get('refresh_token'):
        print("✗ CRÍTICO: Token não possui refresh_token")
        print("  Sem refresh_token, o token expirará em 1 hora")
        print()
        print("Solução: Regenerar o token")
        print("  python config/generate_youtube_token.py")
        return False
    
    print("✓ Refresh token presente")
    
    # Exibir informações
    print()
    print("Informações do Token:")
    print(f"  - Access Token: {'*' * 10}{token_data['token'][-10:]}")
    print(f"  - Refresh Token: {'*' * 10}{token_data['refresh_token'][-10:]}")
    print(f"  - Client ID: {token_data['client_id'][:20]}...")
    print(f"  - Scopes: {', '.join(token_data['scopes'])}")
    
    # Informações do arquivo
    file_stats = os.stat(token_path)
    modified_time = datetime.fromtimestamp(file_stats.st_mtime)
    created_time = datetime.fromtimestamp(file_stats.st_ctime)
    
    print()
    print("Informações do Arquivo:")
    print(f"  - Criado em: {created_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  - Modificado em: {modified_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  - Tamanho: {file_stats.st_size} bytes")
    
    return True

def test_token_with_api():
    """Testa o token fazendo uma chamada à API do YouTube"""
    print()
    print("-" * 70)
    print("TESTANDO TOKEN COM A API DO YOUTUBE")
    print("-" * 70)
    
    try:
        from video.youtube_publisher import YouTubePublisher
        
        publisher = YouTubePublisher()
        
        print("\nAutenticando...")
        if publisher.authenticate():
            print("✓ Autenticação bem-sucedida!")
            
            # Tentar listar canais
            try:
                response = publisher.youtube.channels().list(
                    part='snippet,statistics',
                    mine=True
                ).execute()
                
                if 'items' in response and len(response['items']) > 0:
                    channel = response['items'][0]
                    snippet = channel['snippet']
                    stats = channel.get('statistics', {})
                    
                    print()
                    print("✓ Conexão com a API funcionando!")
                    print()
                    print("Informações do Canal:")
                    print(f"  - Nome: {snippet.get('title', 'N/A')}")
                    print(f"  - Descrição: {snippet.get('description', 'N/A')[:100]}...")
                    print(f"  - Inscritos: {stats.get('subscriberCount', 'N/A')}")
                    print(f"  - Vídeos: {stats.get('videoCount', 'N/A')}")
                    print(f"  - Visualizações: {stats.get('viewCount', 'N/A')}")
                    
                    return True
                else:
                    print("⚠️ Token autenticado, mas nenhum canal encontrado")
                    print("   Verifique se a conta tem um canal do YouTube associado")
                    return False
                    
            except Exception as api_error:
                print(f"✗ Erro ao chamar a API: {str(api_error)}")
                return False
        else:
            print("✗ Falha na autenticação")
            print()
            print("Possíveis causas:")
            print("  - Token expirou ou foi revogado")
            print("  - client_secret.json inválido")
            print("  - Problemas de conexão")
            print()
            print("Solução: Regenerar o token")
            print("  python config/generate_youtube_token.py")
            return False
            
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False

def main():
    # Verificar arquivo de token
    if not check_token_file():
        print()
        print("=" * 70)
        print("RESULTADO: Token inválido ou não encontrado")
        print("=" * 70)
        sys.exit(1)
    
    # Testar com a API
    if test_token_with_api():
        print()
        print("=" * 70)
        print("✓ RESULTADO: Token válido e funcionando!")
        print("=" * 70)
        print()
        print("Lembre-se:")
        print("  - Tokens expiram após ~6 meses de inatividade")
        print("  - Execute este script periodicamente para verificar")
        print("  - Se o token expirar, execute: python config/generate_youtube_token.py")
        print()
        sys.exit(0)
    else:
        print()
        print("=" * 70)
        print("✗ RESULTADO: Token com problemas")
        print("=" * 70)
        print()
        print("Execute para regenerar:")
        print("  python config/generate_youtube_token.py")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()

