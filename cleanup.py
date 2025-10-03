#!/usr/bin/env python3
"""
Script para limpeza manual de arquivos temporários
"""
import sys
from bible_video_generator import BibleVideoGenerator

def main():
    """Executa limpeza de arquivos temporários"""
    generator = BibleVideoGenerator()
    
    print("LIMPEZA DE ARQUIVOS TEMPORÁRIOS")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Limpeza específica de um livro
        book_name = sys.argv[1].lower().replace(' ', '-')
        generator.manual_cleanup(book_name)
    else:
        # Limpeza geral
        print("Este comando irá remover todos os arquivos temporários:")
        print("- Textos gerados")
        print("- Áudios de narração")
        print("- Vídeos do Pexels")
        print("- Vídeo final")
        print("- Legendas")
        print("- Música de fundo")
        
        confirm = input("\nContinuar? (s/n): ").strip().lower()
        if confirm == 's':
            generator.manual_cleanup()
        else:
            print("Limpeza cancelada.")

if __name__ == "__main__":
    main()
