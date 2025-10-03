"""
Gerador de texto bíblico completo
"""
import requests
import json
from typing import Dict, List

class BibleTextGenerator:
    def __init__(self):
        self.base_url = "https://bible-api.com"
        
    def get_book_chapters(self, book_name: str) -> Dict:
        """
        Obtém informações sobre os capítulos de um livro bíblico
        """
        response = requests.get(f"{self.base_url}/{book_name}")
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_chapter_text(self, book_name: str, chapter: int) -> str:
        """
        Obtém o texto de um capítulo específico
        """
        response = requests.get(f"{self.base_url}/{book_name}+{chapter}")
        if response.status_code == 200:
            data = response.json()
            return data.get('text', '')
        return ''
    
    def get_full_book_text(self, book_name: str) -> str:
        """
        Obtém o texto completo de um livro bíblico
        """
        book_info = self.get_book_chapters(book_name)
        if not book_info:
            return ''
        
        chapters = book_info.get('verses', [])
        full_text = f"Livro de {book_name.upper()}\n\n"
        
        for verse in chapters:
            chapter_num = verse.get('chapter', 1)
            verse_text = verse.get('text', '')
            full_text += f"Capítulo {chapter_num}\n\n{verse_text}\n\n"
        
        return full_text
    
    def get_available_books(self) -> List[str]:
        """
        Retorna lista de livros bíblicos disponíveis
        """
        books = [
            "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
            "joshua", "judges", "ruth", "1-samuel", "2-samuel",
            "1-kings", "2-kings", "1-chronicles", "2-chronicles", "ezra",
            "nehemiah", "esther", "job", "psalms", "proverbs",
            "ecclesiastes", "song-of-songs", "isaiah", "jeremiah", "lamentations",
            "ezekiel", "daniel", "hosea", "joel", "amos",
            "obadiah", "jonah", "micah", "nahum", "habakkuk",
            "zephaniah", "haggai", "zechariah", "malachi",
            "matthew", "mark", "luke", "john", "acts",
            "romans", "1-corinthians", "2-corinthians", "galatians", "ephesians",
            "philippians", "colossians", "1-thessalonians", "2-thessalonians", "1-timothy",
            "2-timothy", "titus", "philemon", "hebrews", "james",
            "1-peter", "2-peter", "1-john", "2-john", "3-john",
            "jude", "revelation"
        ]
        return books

def main():
    generator = BibleTextGenerator()
    books = generator.get_available_books()
    
    print("Livros bíblicos disponíveis:")
    for i, book in enumerate(books, 1):
        print(f"{i}. {book}")
    
    choice = input("\nDigite o número do livro ou o nome: ")
    
    if choice.isdigit():
        book_name = books[int(choice) - 1]
    else:
        book_name = choice.lower().replace(' ', '-')
    
    print(f"\nGerando texto do livro: {book_name}")
    text = generator.get_full_book_text(book_name)
    
    if text:
        # Salvar em arquivo
        with open(f'{book_name}_text.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Texto salvo em: {book_name}_text.txt")
        print(f"Tamanho do texto: {len(text)} caracteres")
    else:
        print("Erro ao gerar texto do livro.")

if __name__ == "__main__":
    main()
