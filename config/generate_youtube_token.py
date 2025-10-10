#!/usr/bin/env python3
"""
Script para gerar token.json do YouTube em formato correto
Execute este script localmente para autenticar e gerar o token.json
Depois copie o conteúdo do token.json para o GitHub Secret YOUTUBE_TOKEN
"""

import os
import sys
import json
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video.youtube_publisher import YouTubePublisher

def validate_token(token_file):
    """Valida se o token possui todos os campos necessários"""
    try:
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        missing_fields = [field for field in required_fields if field not in token_data]
        
        if missing_fields:
            print(f"\n⚠️ AVISO: Token gerado está incompleto. Campos faltando: {', '.join(missing_fields)}")
            return False
        
        if not token_data.get('refresh_token'):
            print("\n⚠️ AVISO CRÍTICO: Token não possui refresh_token!")
            print("Sem refresh_token, o token expirará em 1 hora e não poderá ser renovado automaticamente.")
            return False
        
        print("\n✓ Token validado com sucesso!")
        print(f"  - Access Token: {'*' * 10}{token_data['token'][-10:]}")
        print(f"  - Refresh Token: {'*' * 10}{token_data['refresh_token'][-10:]}")
        print(f"  - Client ID: {token_data['client_id'][:20]}...")
        print(f"  - Scopes: {', '.join(token_data['scopes'])}")
        
        return True
        
    except json.JSONDecodeError:
        print("\n✗ Erro: Token não é um JSON válido")
        return False
    except Exception as e:
        print(f"\n✗ Erro ao validar token: {str(e)}")
        return False

def test_token(publisher):
    """Testa se o token funciona fazendo uma chamada simples à API"""
    try:
        print("\nTestando token com a API do YouTube...")
        
        # Tentar listar canais (operação simples que não modifica nada)
        response = publisher.youtube.channels().list(
            part='snippet',
            mine=True
        ).execute()
        
        if 'items' in response and len(response['items']) > 0:
            channel = response['items'][0]
            channel_title = channel['snippet']['title']
            print(f"✓ Token funcionando! Canal: {channel_title}")
            return True
        else:
            print("⚠️ Token autenticado, mas nenhum canal encontrado")
            return True
            
    except Exception as e:
        error_str = str(e)
        
        # Verificar se é erro de escopo insuficiente
        if 'insufficient authentication scopes' in error_str.lower() or 'insufficientpermissions' in error_str.lower():
            print("⚠️ Token tem escopo limitado (apenas upload)")
            print("   Isso é normal se você gerou o token anteriormente.")
            print("   O token FUNCIONA para upload de vídeos!")
            print()
            print("   Para validação completa, regenere o token:")
            print("   1. Delete config/token.json")
            print("   2. Execute este script novamente")
            return True  # Token é válido para upload mesmo sem scope de leitura
        
        print(f"✗ Erro ao testar token: {error_str}")
        return False

def main():
    print("=" * 70)
    print("GERADOR DE TOKEN DO YOUTUBE")
    print("=" * 70)
    print()
    print("Este script irá:")
    print("1. Abrir seu navegador para autenticação do YouTube")
    print("2. Gerar o arquivo config/token.json")
    print("3. Validar o token gerado")
    print("4. Testar o token com a API do YouTube")
    print("5. Mostrar o conteúdo para você copiar para o GitHub Secret")
    print()
    print("IMPORTANTE: Certifique-se de que:")
    print("  - O arquivo config/client_secret.json existe")
    print("  - Você está autenticando com a conta correta do YouTube")
    print("  - A YouTube Data API v3 está ativada no Google Cloud")
    print()
    
    input("Pressione Enter para continuar...")
    
    # Verificar se client_secret.json existe
    client_secret_path = 'config/client_secret.json'
    if not os.path.exists(client_secret_path):
        print(f"\n✗ ERRO: {client_secret_path} não encontrado!")
        print("\nComo obter o client_secret.json:")
        print("1. Acesse: https://console.cloud.google.com/")
        print("2. Crie/selecione seu projeto")
        print("3. Ative a YouTube Data API v3")
        print("4. Crie credenciais OAuth 2.0")
        print("5. Baixe e salve como config/client_secret.json")
        sys.exit(1)
    
    # Remover token antigo se existir
    token_path = 'config/token.json'
    if os.path.exists(token_path):
        print(f"\nToken antigo encontrado em {token_path}")
        resposta = input("Deseja removê-lo e gerar um novo? (s/N): ").strip().lower()
        if resposta == 's':
            try:
                os.remove(token_path)
                print("✓ Token antigo removido")
            except Exception as e:
                print(f"✗ Erro ao remover token antigo: {str(e)}")
        else:
            print("Operação cancelada. Token antigo mantido.")
            sys.exit(0)
    
    # Criar publisher e autenticar
    publisher = YouTubePublisher()
    
    print("\nAutenticando com o YouTube...")
    print("(Uma janela do navegador será aberta)")
    
    if publisher.authenticate():
        print("\n" + "=" * 70)
        print("✓ AUTENTICAÇÃO BEM-SUCEDIDA!")
        print("=" * 70)
        print(f"✓ Token salvo em: {publisher.token_file}")
        
        # Validar token
        if not validate_token(publisher.token_file):
            print("\n⚠️ Token gerado com problemas. Considere regenerar.")
        
        # Testar token
        if not test_token(publisher):
            print("\n⚠️ Token não passou no teste da API.")
        
        # Ler e exibir o conteúdo do token
        with open(publisher.token_file, 'r') as f:
            token_content = f.read()
        
        print("\n" + "=" * 70)
        print("CONTEÚDO DO TOKEN (copie tudo abaixo):")
        print("=" * 70)
        print(token_content)
        print("=" * 70)
        
        print("\nPRÓXIMOS PASSOS:")
        print("1. Copie TODO o conteúdo acima (incluindo { e })")
        print("2. Vá para: GitHub → Settings → Secrets and variables → Actions")
        print("3. Encontre ou crie o secret: YOUTUBE_TOKEN")
        print("4. Cole o conteúdo copiado")
        print("5. Salve!")
        print()
        print("DICA: Para copiar facilmente, você pode:")
        print(f"  - Abrir o arquivo: {publisher.token_file}")
        print("  - Ou usar: cat config/token.json | clip (Windows)")
        print("  - Ou usar: cat config/token.json | pbcopy (Mac)")
        print()
        print("⚠️ LEMBRE-SE:")
        print("  - Tokens expiram após ~6 meses de inatividade")
        print("  - Quando expirar, execute este script novamente")
        print("  - Consulte config/YOUTUBE_TOKEN_GUIDE.md para mais informações")
        print()
        
    else:
        print("\n" + "=" * 70)
        print("✗ ERRO NA AUTENTICAÇÃO")
        print("=" * 70)
        print("\nPossíveis causas:")
        print("  - client_secret.json inválido ou corrompido")
        print("  - YouTube Data API v3 não está ativada")
        print("  - Problemas de conexão com a internet")
        print("  - Navegador bloqueou a autenticação")
        print()
        print("Consulte: config/YOUTUBE_TOKEN_GUIDE.md para ajuda")
        sys.exit(1)

if __name__ == "__main__":
    main()

