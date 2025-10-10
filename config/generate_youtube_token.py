#!/usr/bin/env python3
"""
Script para gerar token.json do YouTube em formato correto
Execute este script localmente para autenticar e gerar o token.json
Depois copie o conteúdo do token.json para o GitHub Secret YOUTUBE_TOKEN
"""

import os
import sys
import json

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video.youtube_publisher import YouTubePublisher

def main():
    print("=" * 70)
    print("GERADOR DE TOKEN DO YOUTUBE")
    print("=" * 70)
    print()
    print("Este script irá:")
    print("1. Abrir seu navegador para autenticação do YouTube")
    print("2. Gerar o arquivo config/token.json")
    print("3. Mostrar o conteúdo para você copiar para o GitHub Secret")
    print()
    
    input("Pressione Enter para continuar...")
    
    # Criar publisher e autenticar
    publisher = YouTubePublisher()
    
    print("\nAutenticando com o YouTube...")
    if publisher.authenticate():
        print("\n✓ Autenticação bem-sucedida!")
        print(f"✓ Token salvo em: {publisher.token_file}")
        
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
        print("2. Vá para GitHub → Settings → Secrets → Actions")
        print("3. Edite o secret YOUTUBE_TOKEN")
        print("4. Cole o conteúdo copiado")
        print("5. Salve!")
        
    else:
        print("\n✗ Erro na autenticação")
        sys.exit(1)

if __name__ == "__main__":
    main()

