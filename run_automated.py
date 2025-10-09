#!/usr/bin/env python3
"""
Script de execução automatizada para GitHub Actions
Escolhe livro bíblico aleatoriamente e gera vídeo
"""

import os
import sys
import random
from datetime import datetime
from video.video_generation_orchestrator import VideoGenerationOrchestrator
from config.config import video_config


# Lista dos 66 livros da Bíblia
BIBLE_BOOKS = [
    'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy',
    'joshua', 'judges', 'ruth', '1_samuel', '2_samuel',
    '1_kings', '2_kings', '1_chronicles', '2_chronicles', 'ezra',
    'nehemiah', 'esther', 'job', 'psalms', 'proverbs',
    'ecclesiastes', 'song_of_songs', 'isaiah', 'jeremiah', 'lamentations',
    'ezekiel', 'daniel', 'hosea', 'joel', 'amos',
    'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk',
    'zephaniah', 'haggai', 'zechariah', 'malachi',
    'matthew', 'mark', 'luke', 'john', 'acts',
    'romans', '1_corinthians', '2_corinthians', 'galatians', 'ephesians',
    'philippians', 'colossians', '1_thessalonians', '2_thessalonians', '1_timothy',
    '2_timothy', 'titus', 'philemon', 'hebrews', 'james',
    '1_peter', '2_peter', '1_john', '2_john', '3_john',
    'jude', 'revelation'
]


def select_book():
    """Seleciona livro: por argumento, variável de ambiente ou aleatório"""
    
    # Via argumento da linha de comando
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        
        if arg.isdigit():
            number = int(arg)
            if 1 <= number <= 66:
                book = BIBLE_BOOKS[number - 1]
                print(f"[NÚMERO] Livro #{number}: {book}")
                return book
        
        book = arg.lower().replace(' ', '_')
        if book in BIBLE_BOOKS:
            print(f"[NOME] Livro: {book}")
            return book
    
    # Via variável de ambiente BOOK_NUMBER
    book_number = os.getenv('BOOK_NUMBER')
    if book_number and book_number.isdigit():
        number = int(book_number)
        if 1 <= number <= 66:
            book = BIBLE_BOOKS[number - 1]
            print(f"[ENV BOOK_NUMBER] Livro #{number}: {book}")
            return book
    
    # Via variável de ambiente BOOK_NAME
    book_name = os.getenv('BOOK_NAME')
    if book_name:
        book = book_name.lower().replace(' ', '_')
        if book in BIBLE_BOOKS:
            print(f"[ENV BOOK_NAME] Livro: {book}")
            return book
    
    # Aleatório (padrão)
    book = random.choice(BIBLE_BOOKS)
    print(f"[ALEATÓRIO] Livro sorteado: {book}")
    return book


def main():
    """Execução principal"""
    try:
        print("=" * 70)
        print("EXECUÇÃO AUTOMATIZADA - GERADOR DE VÍDEOS BÍBLICOS")
        print("=" * 70)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Validar PEXELS_API_KEY
        pexels_key = os.getenv('PEXELS_API_KEY')
        if not pexels_key:
            print("ERRO: PEXELS_API_KEY não configurada")
            sys.exit(1)
        
        # Selecionar livro
        book_name = select_book()
        
        # Configurações
        print(f"Idioma: {video_config.get('language', 'en')}")
        print(f"Velocidade: {video_config.get('voice_speed', 1.0)}x")
        
        # Verificar auto-publicação
        youtube_settings = video_config.get('youtube_settings', {})
        auto_publish = youtube_settings.get('auto_publish', False)
        publish = os.getenv('AUTO_PUBLISH', str(auto_publish)).lower() in ['true', '1', 'yes']
        
        print(f"Auto-publicação: {'SIM' if publish else 'NÃO'}")
        print("=" * 70)
        
        # Gerar vídeo
        orchestrator = VideoGenerationOrchestrator()
        result = orchestrator._generate_video(book_name, publish, pexels_key)
        
        if result:
            print("\n" + "=" * 70)
            print("✓ SUCESSO! Vídeo gerado")
            print(f"  Arquivo: {result}")
            print("=" * 70)
            orchestrator._cleanup_after_success(book_name)
            sys.exit(0)
        else:
            print("\n✗ ERRO: Falha na geração")
            orchestrator._cleanup_after_failure(book_name)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠ Processo interrompido")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n✗ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

