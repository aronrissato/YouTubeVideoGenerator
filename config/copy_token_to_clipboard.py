#!/usr/bin/env python3
"""
Script auxiliar para copiar o token do YouTube para a área de transferência
Útil para facilitar a atualização do GitHub Secret
"""

import os
import sys
import json

def copy_to_clipboard(text):
    """Tenta copiar texto para a área de transferência"""
    try:
        # Windows
        if sys.platform == 'win32':
            import subprocess
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            process.communicate(text.encode('utf-8'))
            return True
        
        # macOS
        elif sys.platform == 'darwin':
            import subprocess
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        
        # Linux com xclip
        elif sys.platform.startswith('linux'):
            try:
                import subprocess
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
                return True
            except FileNotFoundError:
                # Tentar com xsel
                try:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                    process.communicate(text.encode('utf-8'))
                    return True
                except FileNotFoundError:
                    return False
        
        return False
        
    except Exception as e:
        print(f"Erro ao copiar para área de transferência: {str(e)}")
        return False

def main():
    token_path = 'config/token.json'
    
    print("=" * 70)
    print("COPIAR TOKEN DO YOUTUBE PARA ÁREA DE TRANSFERÊNCIA")
    print("=" * 70)
    print()
    
    # Verificar se o token existe
    if not os.path.exists(token_path):
        print(f"✗ Token não encontrado em: {token_path}")
        print()
        print("Para gerar um token:")
        print("  python config/generate_youtube_token.py")
        sys.exit(1)
    
    # Ler o token
    try:
        with open(token_path, 'r', encoding='utf-8') as f:
            token_content = f.read()
        
        # Validar JSON
        try:
            token_data = json.loads(token_content)
            
            # Verificar campos obrigatórios
            required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
            missing_fields = [field for field in required_fields if field not in token_data]
            
            if missing_fields:
                print(f"⚠️ AVISO: Token incompleto. Campos faltando: {', '.join(missing_fields)}")
                print()
            
            print("✓ Token encontrado e validado")
            print()
            print("Informações do Token:")
            print(f"  - Access Token: {'*' * 10}{token_data.get('token', '')[-10:]}")
            print(f"  - Refresh Token: {'*' * 10}{token_data.get('refresh_token', '')[-10:]}")
            print(f"  - Client ID: {token_data.get('client_id', '')[:20]}...")
            
        except json.JSONDecodeError:
            print("⚠️ AVISO: Token não é um JSON válido")
            print()
        
        # Tentar copiar para a área de transferência
        print()
        print("Tentando copiar para área de transferência...")
        
        if copy_to_clipboard(token_content):
            print("✓ Token copiado para área de transferência com sucesso!")
            print()
            print("PRÓXIMOS PASSOS:")
            print("1. Vá para: GitHub → Settings → Secrets and variables → Actions")
            print("2. Encontre ou crie o secret: YOUTUBE_TOKEN")
            print("3. Cole o conteúdo (Ctrl+V ou Cmd+V)")
            print("4. Salve!")
        else:
            print("✗ Não foi possível copiar automaticamente")
            print()
            print("INSTRUÇÕES MANUAIS:")
            print(f"1. Abra o arquivo: {token_path}")
            print("2. Copie TODO o conteúdo (Ctrl+A, Ctrl+C)")
            print("3. Vá para: GitHub → Settings → Secrets and variables → Actions")
            print("4. Encontre ou crie o secret: YOUTUBE_TOKEN")
            print("5. Cole o conteúdo (Ctrl+V)")
            print("6. Salve!")
            print()
            print("Ou exiba o conteúdo aqui:")
            exibir = input("Deseja exibir o conteúdo do token? (s/N): ").strip().lower()
            if exibir == 's':
                print()
                print("=" * 70)
                print("CONTEÚDO DO TOKEN:")
                print("=" * 70)
                print(token_content)
                print("=" * 70)
        
        print()
        print("=" * 70)
        print("✓ CONCLUÍDO")
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ Erro ao ler token: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

