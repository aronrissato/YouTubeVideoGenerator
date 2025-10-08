#!/usr/bin/env python3
"""
Script para calcular e exibir durações por capítulo de um livro bíblico
"""

import json
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import video_config

def calculate_duration(text: str, voice_speed: float, language: str) -> dict:
    """Calcula a duração estimada de um texto"""
    char_count = len(text.strip())
    
    # Palavras por minuto padrão por idioma (velocidade 1.0x)
    base_wpm = {
        'pt': 150, 'pt-BR': 150, 'pt-pt': 150,
        'en': 160, 'en-US': 160, 'en-GB': 160,
        'es': 155, 'fr': 150, 'de': 150, 'it': 150
    }
    
    words_per_minute = base_wpm.get(language, 160) * voice_speed
    estimated_words = char_count / 5
    duration_minutes = estimated_words / words_per_minute
    duration_seconds = duration_minutes * 60
    
    return {
        'char_count': char_count,
        'estimated_words': int(estimated_words),
        'duration_minutes': duration_minutes,
        'duration_seconds': duration_seconds,
        'words_per_minute': words_per_minute
    }

def analyze_book(book_name: str):
    """Analisa um livro e mostra durações por capítulo"""
    bible_data_dir = Path(__file__).parent
    filename = f"{book_name.lower().replace(' ', '_').replace('-', '_')}.json"
    filepath = bible_data_dir / filename
    
    if not filepath.exists():
        print(f"ERRO: Arquivo {filename} não encontrado")
        return
    
    # Carregar dados do livro
    with open(filepath, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    
    verses = book_data.get('verses', [])
    if not verses:
        print("ERRO: Nenhum versículo encontrado")
        return
    
    # Obter configurações
    voice_speed = video_config.get('voice_speed', 1.0)
    language = video_config.get('language', 'en')
    
    # Agrupar versículos por capítulo
    chapters = {}
    for verse in verses:
        chapter = verse.get('chapter', 1)
        if chapter not in chapters:
            chapters[chapter] = []
        chapters[chapter].append(verse.get('text', ''))
    
    print("=" * 80)
    print(f"ANÁLISE DE DURAÇÃO: {book_data.get('reference', book_name).upper()}")
    print("=" * 80)
    print(f"Idioma: {language}")
    print(f"Velocidade da voz: {voice_speed}x")
    print(f"Total de capítulos: {len(chapters)}")
    print(f"Total de versículos: {len(verses)}")
    print("=" * 80)
    print()
    
    # Calcular duração de cada capítulo
    total_duration_seconds = 0
    
    for chapter_num in sorted(chapters.keys()):
        chapter_text = ' '.join(chapters[chapter_num])
        duration_info = calculate_duration(chapter_text, voice_speed, language)
        
        total_duration_seconds += duration_info['duration_seconds']
        
        # Formatar duração
        minutes = int(duration_info['duration_minutes'])
        seconds = int(duration_info['duration_seconds'] % 60)
        
        print(f"Capítulo {chapter_num}:")
        print(f"  - Caracteres: {duration_info['char_count']:,}")
        print(f"  - Palavras estimadas: {duration_info['estimated_words']:,}")
        print(f"  - Duração: {minutes}m {seconds}s ({duration_info['duration_seconds']:.1f}s)")
        print()
    
    # Duração total
    total_minutes = int(total_duration_seconds / 60)
    total_seconds = int(total_duration_seconds % 60)
    
    print("=" * 80)
    print("DURAÇÃO TOTAL DO LIVRO COMPLETO:")
    print(f"  - {total_minutes}m {total_seconds}s ({total_duration_seconds:.1f}s)")
    
    if total_duration_seconds < 60:
        print(f"  - {total_duration_seconds:.1f} segundos")
    elif total_duration_seconds < 3600:
        print(f"  - {total_duration_seconds/60:.1f} minutos")
    else:
        hours = int(total_duration_seconds / 3600)
        minutes = int((total_duration_seconds % 3600) / 60)
        print(f"  - {hours}h {minutes}m")
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        print("Uso: python calculate_chapter_durations.py [nome-do-livro]")
        print("Exemplo: python calculate_chapter_durations.py philippians")
        sys.exit(1)
    
    book_name = sys.argv[1]
    analyze_book(book_name)

if __name__ == "__main__":
    main()

