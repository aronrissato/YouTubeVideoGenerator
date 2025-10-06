#!/usr/bin/env python3
"""
Script para calcular e salvar as durações dos livros bíblicos
Este script processa todos os arquivos JSON da pasta bible_data e adiciona
informações de duração estimada para cada livro.
"""

import json
import os
import sys
from pathlib import Path

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from config.config import video_config

def calculate_book_duration(text: str) -> dict:
    """
    Calcula a duração estimada de um livro bíblico baseado no texto
    """
    try:
        # Contar caracteres (sem espaços em branco extras)
        char_count = len(text.strip())
        
        # Configurações de velocidade da voz
        voice_speed = video_config.config.get('voice_speed', 1.0)
        
        # Palavras por minuto baseadas no idioma e velocidade
        language = video_config.config.get('language', 'en')
        
        # Palavras por minuto padrão por idioma (velocidade 1.0x)
        base_wpm = {
            'pt': 150, 'pt-BR': 150, 'pt-pt': 150,
            'en': 160, 'en-US': 160, 'en-GB': 160,
            'es': 155, 'fr': 150, 'de': 150, 'it': 150
        }
        
        words_per_minute = base_wpm.get(language, 160) * voice_speed
        
        # Estimar palavras baseado em caracteres (aproximadamente 5 caracteres por palavra)
        estimated_words = char_count / 5
        
        # Calcular duração em minutos
        duration_minutes = estimated_words / words_per_minute
        
        # Formatar duração para exibição
        if duration_minutes < 1:
            duration_text = f"{int(duration_minutes * 60)}s"
        elif duration_minutes < 60:
            duration_text = f"{duration_minutes:.1f}min"
        else:
            hours = int(duration_minutes // 60)
            minutes = int(duration_minutes % 60)
            duration_text = f"{hours}h{minutes:02d}min"
        
        # Determinar status baseado na duração
        if duration_minutes < 5:
            status = "Curto"
        elif duration_minutes < 30:
            status = "Médio"
        elif duration_minutes < 60:
            status = "Longo"
        else:
            status = "Muito Longo"
        
        return {
            'duration_text': duration_text,
            'status': status,
            'duration_minutes': round(duration_minutes, 2),
            'char_count': char_count,
            'estimated_words': round(estimated_words, 0),
            'words_per_minute': words_per_minute
        }
        
    except Exception as e:
        return {
            'duration_text': 'Erro',
            'status': 'Erro',
            'duration_minutes': 0,
            'char_count': 0,
            'estimated_words': 0,
            'words_per_minute': 0,
            'error': str(e)
        }

def get_chapter_count(verses: list) -> int:
    """
    Conta o número de capítulos únicos em uma lista de versículos
    """
    chapters = set()
    for verse in verses:
        if 'chapter' in verse:
            chapters.add(verse['chapter'])
    return len(chapters)

def process_book_file(file_path: str) -> bool:
    """
    Processa um arquivo JSON de livro bíblico e adiciona informações de duração
    """
    try:
        print(f"Processando: {os.path.basename(file_path)}")
        
        # Ler arquivo JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        
        # Extrair texto completo
        text_parts = []
        for verse in book_data.get('verses', []):
            if 'text' in verse:
                text_parts.append(verse['text'].strip())
        
        full_text = ' '.join(text_parts)
        
        # Calcular duração
        duration_info = calculate_book_duration(full_text)
        
        # Contar capítulos
        chapter_count = get_chapter_count(book_data.get('verses', []))
        
        # Adicionar informações de duração ao arquivo
        book_data['metadata'] = {
            'chapter_count': chapter_count,
            'verse_count': len(book_data.get('verses', [])),
            'duration': duration_info,
            'last_updated': str(Path(file_path).stat().st_mtime)
        }
        
        # Salvar arquivo atualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ {book_data.get('reference', 'Unknown')}: {chapter_count} capítulos, {duration_info['duration_text']}")
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao processar {file_path}: {e}")
        return False

def main():
    """
    Função principal para processar todos os arquivos JSON
    """
    bible_data_dir = Path(__file__).parent
    
    print("Calculando durações dos livros bíblicos...")
    print("=" * 60)
    
    # Encontrar todos os arquivos JSON
    json_files = list(bible_data_dir.glob("*.json"))
    
    if not json_files:
        print("Nenhum arquivo JSON encontrado na pasta bible_data/")
        return
    
    print(f"Encontrados {len(json_files)} arquivos para processar")
    print()
    
    success_count = 0
    total_count = len(json_files)
    
    for json_file in sorted(json_files):
        if process_book_file(str(json_file)):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Processamento concluído: {success_count}/{total_count} arquivos processados com sucesso")
    
    if success_count == total_count:
        print("✓ Todos os livros foram processados com sucesso!")
    else:
        print(f"⚠ {total_count - success_count} arquivos falharam no processamento")

if __name__ == "__main__":
    main()
