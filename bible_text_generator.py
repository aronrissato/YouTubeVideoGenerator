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
            try:
                data = response.json()
                # Verificar se realmente retornou o capítulo solicitado
                verses = data.get('verses', [])
                if verses:
                    first_verse = verses[0]
                    returned_chapter = first_verse.get('chapter', 0)
                    if returned_chapter == chapter:
                        return data.get('text', '')
            except:
                pass
        return ''
    
    def detect_chapter_count(self, book_name: str) -> int:
        """
        Detecta automaticamente o número de capítulos de um livro
        """
        # Primeiro, verificar se o capítulo 1 existe
        if not self.get_chapter_text(book_name, 1):
            return 0
        
        # Usar busca binária para encontrar o último capítulo
        low = 1
        high = 200  # Limite máximo
        last_found = 1
        
        while low <= high:
            mid = (low + high) // 2
            test_text = self.get_chapter_text(book_name, mid)
            
            if test_text:
                last_found = mid
                low = mid + 1
            else:
                high = mid - 1
        
        return last_found
    
    def get_full_book_text(self, book_name: str) -> str:
        """
        Obtém o texto completo de um livro bíblico
        """
        # Normalizar nome do livro
        book_name = book_name.lower()
        
        # Mapear nomes dos livros para os formatos aceitos pela API
        book_mapping = {
            'genesis': 'Genesis',
            'exodus': 'Exodus', 
            'leviticus': 'Leviticus',
            'numbers': 'Numbers',
            'deuteronomy': 'Deuteronomy',
            'joshua': 'Joshua',
            'judges': 'Judges',
            'ruth': 'Ruth',
            '1-samuel': '1 Samuel',
            '2-samuel': '2 Samuel',
            '1-kings': '1 Kings',
            '2-kings': '2 Kings',
            '1-chronicles': '1 Chronicles',
            '2-chronicles': '2 Chronicles',
            'ezra': 'Ezra',
            'nehemiah': 'Nehemiah',
            'esther': 'Esther',
            'job': 'Job',
            'psalms': 'Psalms',
            'proverbs': 'Proverbs',
            'ecclesiastes': 'Ecclesiastes',
            'song-of-songs': 'Song of Songs',
            'isaiah': 'Isaiah',
            'jeremiah': 'Jeremiah',
            'lamentations': 'Lamentations',
            'ezekiel': 'Ezekiel',
            'daniel': 'Daniel',
            'hosea': 'Hosea',
            'joel': 'Joel',
            'amos': 'Amos',
            'obadiah': 'Obadiah',
            'jonah': 'Jonah',
            'micah': 'Micah',
            'nahum': 'Nahum',
            'habakkuk': 'Habakkuk',
            'zephaniah': 'Zephaniah',
            'haggai': 'Haggai',
            'zechariah': 'Zechariah',
            'malachi': 'Malachi',
            'matthew': 'Matthew',
            'mark': 'Mark',
            'luke': 'Luke',
            'john': 'John',
            'acts': 'Acts',
            'romans': 'Romans',
            '1-corinthians': '1 Corinthians',
            '2-corinthians': '2 Corinthians',
            'galatians': 'Galatians',
            'ephesians': 'Ephesians',
            'philippians': 'Philippians',
            'colossians': 'Colossians',
            '1-thessalonians': '1 Thessalonians',
            '2-thessalonians': '2 Thessalonians',
            '1-timothy': '1 Timothy',
            '2-timothy': '2 Timothy',
            'titus': 'Titus',
            'philemon': 'Philemon',
            'hebrews': 'Hebrews',
            'james': 'James',
            '1-peter': '1 Peter',
            '2-peter': '2 Peter',
            '1-john': '1 John',
            '2-john': '2 John',
            '3-john': '3 John',
            'jude': 'Jude',
            'revelation': 'Revelation'
        }
        
        # Obter nome formatado para a API
        api_book_name = book_mapping.get(book_name, book_name.title())
        
        print(f"Detectando número de capítulos para {api_book_name}...")
        chapter_count = self.detect_chapter_count(api_book_name)
        
        if chapter_count == 0:
            print(f"ERRO: Nenhum capítulo encontrado para {api_book_name}")
            return ''
        
        print(f"Encontrados {chapter_count} capítulos para {api_book_name}")
        full_text = f"Livro de {api_book_name.upper()}\n\n"
        
        # Buscar cada capítulo
        for chapter_num in range(1, chapter_count + 1):
            print(f"Buscando capítulo {chapter_num}/{chapter_count}...")
            chapter_text = self.get_chapter_text(api_book_name, chapter_num)
            if chapter_text:
                full_text += f"Capítulo {chapter_num}\n\n{chapter_text}\n\n"
            else:
                print(f"Aviso: Capítulo {chapter_num} não encontrado")
        
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
