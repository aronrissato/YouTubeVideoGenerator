#!/usr/bin/env python3
"""
Criador de dados em inglês para livros da bíblia
"""
import os
import json

def create_english_bible_book(book_name: str, chapter_texts: dict):
    """Cria dados em inglês para um livro da bíblia"""
    
    # Criar diretório
    bible_dir = "bible_data"
    if not os.path.exists(bible_dir):
        os.makedirs(bible_dir)
    
    # Estrutura do livro
    book_data = {
        "reference": book_name,
        "verses": [],
        "text": ""
    }
    
    # Criar versículos para cada capítulo
    for chapter, text in chapter_texts.items():
        # Dividir o texto em versículos (aproximadamente)
        sentences = text.split('. ')
        verse_num = 1
        
        for sentence in sentences:
            if sentence.strip():
                verse_text = sentence.strip()
                if not verse_text.endswith('.'):
                    verse_text += '.'
                
                book_data["verses"].append({
                    "chapter": chapter,
                    "verse": verse_num,
                    "text": verse_text
                })
                verse_num += 1
    
    # Criar texto completo
    book_data["text"] = " ".join([v["text"] for v in book_data["verses"]])
    
    # Salvar arquivo
    filename = f"{book_name.replace(' ', '_').lower()}.json"
    filepath = os.path.join(bible_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] English {book_name} data created: {filepath}")
    print(f"[INFO] {len(book_data['verses'])} verses in {len(chapter_texts)} chapters")
    print(f"[INFO] {len(book_data['text'])} characters of text")
    
    return filepath

def main():
    """Função principal para criar livros em inglês"""
    print("ENGLISH BIBLE BOOK CREATOR")
    print("=" * 40)
    print("This tool helps create English Bible data files.")
    print("Currently available: Leviticus (already created)")
    print("=" * 40)
    
    print("\nTo add more books, you can:")
    print("1. Use this script as a template")
    print("2. Add chapter texts for any book")
    print("3. Run the creation function")
    
    print("\nExample usage:")
    print("create_english_bible_book('Genesis', {1: 'In the beginning...', 2: 'And the earth...'})")

if __name__ == "__main__":
    main()
