"""
Gerador de texto bíblico completo
"""
import requests
import json
import os
from typing import Dict, List

class BibleTextGenerator:
    def __init__(self):
        self.base_url = "https://bible-api.com"
        self.local_bible_dir = "bible_data"
        self.use_local = os.path.exists(self.local_bible_dir)
        
        if self.use_local:
            print("[INFO] Usando dados locais da bíblia")
        else:
            print("[INFO] Usando API online da bíblia")
        
    def get_local_book_data(self, book_name: str) -> Dict:
        """Carrega dados de um livro do armazenamento local"""
        filename = f"{book_name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(self.local_bible_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Erro ao carregar arquivo local {filepath}: {str(e)}")
            return None
    
    def get_book_chapters(self, book_name: str) -> Dict:
        """
        Obtém informações sobre os capítulos de um livro bíblico
        """
        # Tentar usar dados locais primeiro
        if self.use_local:
            local_data = self.get_local_book_data(book_name)
            if local_data:
                return local_data
        
        # Fallback para API online
        try:
            response = requests.get(f"{self.base_url}/{book_name}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[ERRO] Falha na API online: {str(e)}")
        
        return None
    
    def get_chapter_text(self, book_name: str, chapter: int) -> str:
        """
        Obtém o texto de um capítulo específico
        """
        # Tentar usar dados locais primeiro
        if self.use_local:
            local_data = self.get_local_book_data(book_name)
            if local_data:
                verses = local_data.get('verses', [])
                chapter_verses = [v for v in verses if v.get('chapter') == chapter]
                if chapter_verses:
                    # Extrair texto dos versículos
                    text_parts = []
                    for verse in chapter_verses:
                        verse_text = verse.get('text', '').strip()
                        if verse_text:
                            text_parts.append(verse_text)
                    return ' '.join(text_parts)
        
        # Fallback para API online
        try:
            response = requests.get(f"{self.base_url}/{book_name}+{chapter}", timeout=10)
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
        except Exception as e:
            print(f"[ERRO] Falha na API online para {book_name} capítulo {chapter}: {str(e)}")
        
        return ''
    
    def detect_chapter_count(self, book_name: str) -> int:
        """
        Detecta automaticamente o número de capítulos de um livro
        """
        # Tentar usar dados locais primeiro
        if self.use_local:
            local_data = self.get_local_book_data(book_name)
            if local_data:
                verses = local_data.get('verses', [])
                if verses:
                    # Encontrar o maior número de capítulo
                    max_chapter = max(verse.get('chapter', 0) for verse in verses)
                    return max_chapter
        
        # Fallback para API online
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
        full_text = ""
        
        # Buscar cada capítulo
        for chapter_num in range(1, chapter_count + 1):
            print(f"Buscando capítulo {chapter_num}/{chapter_count}...")
            chapter_text = self.get_chapter_text(api_book_name, chapter_num)
            if chapter_text:
                full_text += f"Capítulo {chapter_num}\n\n{chapter_text}\n\n"
            else:
                print(f"Aviso: Capítulo {chapter_num} não encontrado")
        
        return full_text
    
    def get_book_metadata(self, book_name: str) -> Dict:
        """
        Obtém metadados de um livro bíblico (capítulos, duração, etc.)
        """
        if self.use_local:
            local_data = self.get_local_book_data(book_name)
            if local_data and 'metadata' in local_data:
                return local_data['metadata']
        
        # Fallback: retornar informações básicas se não houver metadados
        return {
            'chapter_count': 0,
            'verse_count': 0,
            'duration': {
                'duration_text': 'N/A',
                'status': 'N/A',
                'duration_minutes': 0
            }
        }
    
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
    
    # Mapeamento de livros bíblicos com número de capítulos
    book_chapters = {
        'genesis': 50, 'exodus': 40, 'leviticus': 27, 'numbers': 36, 'deuteronomy': 34,
        'joshua': 24, 'judges': 21, 'ruth': 4, '1-samuel': 31, '2-samuel': 24,
        '1-kings': 22, '2-kings': 25, '1-chronicles': 29, '2-chronicles': 36,
        'ezra': 10, 'nehemiah': 13, 'esther': 10, 'job': 42, 'psalms': 150,
        'proverbs': 31, 'ecclesiastes': 12, 'song-of-solomon': 8, 'isaiah': 66,
        'jeremiah': 52, 'lamentations': 5, 'ezekiel': 48, 'daniel': 12,
        'hosea': 14, 'joel': 3, 'amos': 9, 'obadiah': 1, 'jonah': 4,
        'micah': 7, 'nahum': 3, 'habakkuk': 3, 'zephaniah': 3, 'haggai': 2,
        'zechariah': 14, 'malachi': 4, 'matthew': 28, 'mark': 16, 'luke': 24,
        'john': 21, 'acts': 28, 'romans': 16, '1-corinthians': 16, '2-corinthians': 13,
        'galatians': 6, 'ephesians': 6, 'philippians': 4, 'colossians': 4,
        '1-thessalonians': 5, '2-thessalonians': 3, '1-timothy': 6, '2-timothy': 4,
        'titus': 3, 'philemon': 1, 'hebrews': 13, 'james': 5, '1-peter': 5,
        '2-peter': 3, '1-john': 5, '2-john': 1, '3-john': 1, 'jude': 1, 'revelation': 22
    }
    
    print("Livros bíblicos disponíveis:")
    print("-" * 50)
    for i, book in enumerate(books, 1):
        book_name = book.replace('-', ' ').title()
        chapters = book_chapters.get(book, '?')
        print(f"{i:2d}. {book_name} ({chapters} capítulos)")
    
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
