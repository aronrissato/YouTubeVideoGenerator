#!/usr/bin/env python3
"""
Script para baixar todos os livros bíblicos da API bible-api.com
Salva os dados localmente na pasta bible_data para uso offline
"""
import os
import json
import requests
import time
from typing import Dict, List

class BibleBookDownloader:
    def __init__(self):
        self.base_url = "https://bible-api.com"
        self.output_dir = os.path.dirname(os.path.abspath(__file__))
        self.downloaded_books = []
        self.failed_books = []
        
        # Lista completa de livros bíblicos
        self.books = [
            # Antigo Testamento
            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
            "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
            "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
            "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
            "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah", "Lamentations",
            "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
            "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
            "Zephaniah", "Haggai", "Zechariah", "Malachi",
            
            # Novo Testamento
            "Matthew", "Mark", "Luke", "John", "Acts",
            "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
            "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
            "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
            "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
            "Jude", "Revelation"
        ]
        
        # Para teste inicial, usar apenas livros pequenos
        self.test_books = [
            "Ruth", "Obadiah", "Philemon", "2 John", "3 John", "Jude"
        ]
    
    def download_book(self, book_name: str) -> bool:
        """
        Baixa um livro bíblico completo da API, capítulo por capítulo
        """
        try:
            print(f"Baixando {book_name}...")
            
            # Mapeamento de livros com número de capítulos
            book_chapters = {
                'Genesis': 50, 'Exodus': 40, 'Leviticus': 27, 'Numbers': 36, 'Deuteronomy': 34,
                'Joshua': 24, 'Judges': 21, 'Ruth': 4, '1 Samuel': 31, '2 Samuel': 24,
                '1 Kings': 22, '2 Kings': 25, '1 Chronicles': 29, '2 Chronicles': 36,
                'Ezra': 10, 'Nehemiah': 13, 'Esther': 10, 'Job': 42, 'Psalms': 150,
                'Proverbs': 31, 'Ecclesiastes': 12, 'Song of Songs': 8, 'Isaiah': 66,
                'Jeremiah': 52, 'Lamentations': 5, 'Ezekiel': 48, 'Daniel': 12,
                'Hosea': 14, 'Joel': 3, 'Amos': 9, 'Obadiah': 1, 'Jonah': 4,
                'Micah': 7, 'Nahum': 3, 'Habakkuk': 3, 'Zephaniah': 3, 'Haggai': 2,
                'Zechariah': 14, 'Malachi': 4, 'Matthew': 28, 'Mark': 16, 'Luke': 24,
                'John': 21, 'Acts': 28, 'Romans': 16, '1 Corinthians': 16, '2 Corinthians': 13,
                'Galatians': 6, 'Ephesians': 6, 'Philippians': 4, 'Colossians': 4,
                '1 Thessalonians': 5, '2 Thessalonians': 3, '1 Timothy': 6, '2 Timothy': 4,
                'Titus': 3, 'Philemon': 1, 'Hebrews': 13, 'James': 5, '1 Peter': 5,
                '2 Peter': 3, '1 John': 5, '2 John': 1, '3 John': 1, 'Jude': 1, 'Revelation': 22
            }
            
            total_chapters = book_chapters.get(book_name, 0)
            if total_chapters == 0:
                print(f"  [ERRO] {book_name}: Número de capítulos desconhecido")
                self.failed_books.append(book_name)
                return False
            
            all_verses = []
            successful_chapters = 0
            
            # Baixar cada capítulo
            for chapter in range(1, total_chapters + 1):
                try:
                    # Formatar URL para capítulo específico
                    url = f"{self.base_url}/{book_name.replace(' ', '+')}+{chapter}"
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        all_verses.extend(verses)
                        successful_chapters += 1
                    else:
                        print(f"    Capítulo {chapter}: HTTP {response.status_code}")
                    
                    # Pausa entre capítulos para evitar rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"    Capítulo {chapter}: Erro - {str(e)}")
                    continue
            
            if successful_chapters > 0:
                # Consolidar todos os versículos em um arquivo
                consolidated_data = {
                    'reference': book_name,
                    'verses': all_verses
                }
                
                # Salvar arquivo JSON
                filename = f"{book_name.lower().replace(' ', '_')}.json"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
                
                print(f"  [OK] {book_name}: {len(all_verses)} versículos de {successful_chapters}/{total_chapters} capítulos")
                self.downloaded_books.append(book_name)
                return True
            else:
                print(f"  [ERRO] {book_name}: Nenhum capítulo foi baixado com sucesso")
                self.failed_books.append(book_name)
                return False
                
        except Exception as e:
            print(f"  [ERRO] {book_name}: {str(e)}")
            self.failed_books.append(book_name)
            return False
    
    def download_all_books(self, test_mode=False):
        """
        Baixa todos os livros bíblicos
        """
        books_to_download = self.test_books if test_mode else self.books
        
        print("=" * 60)
        print("BAIXADOR DE LIVROS BÍBLICOS")
        print("=" * 60)
        print(f"Fonte: {self.base_url}")
        print(f"Destino: {self.output_dir}")
        print(f"Total de livros: {len(books_to_download)}")
        if test_mode:
            print("MODO TESTE: Baixando apenas livros pequenos")
        print("=" * 60)
        
        start_time = time.time()
        
        for i, book in enumerate(books_to_download, 1):
            print(f"[{i}/{len(books_to_download)}] ", end="")
            success = self.download_book(book)
            
            # Pausa entre downloads para não sobrecarregar a API
            if i < len(books_to_download):
                time.sleep(1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Relatório final
        print("\n" + "=" * 60)
        print("RELATÓRIO FINAL")
        print("=" * 60)
        print(f"Livros baixados com sucesso: {len(self.downloaded_books)}")
        print(f"Livros com erro: {len(self.failed_books)}")
        print(f"Tempo total: {duration:.1f} segundos")
        
        if self.downloaded_books:
            print(f"\nLivros baixados:")
            for book in self.downloaded_books:
                print(f"  [OK] {book}")
        
        if self.failed_books:
            print(f"\nLivros com erro:")
            for book in self.failed_books:
                print(f"  [ERRO] {book}")
        
        print("\n" + "=" * 60)
        
        if len(self.downloaded_books) == len(books_to_download):
            print("SUCESSO! TODOS OS LIVROS FORAM BAIXADOS!")
            print("Agora você pode usar o sistema offline.")
        else:
            print("AVISO: Alguns livros falharam. Execute o script novamente para tentar baixar os que falharam.")
    
    def verify_downloads(self):
        """
        Verifica quais livros já foram baixados
        """
        print("Verificando livros já baixados...")
        
        downloaded = []
        missing = []
        
        for book in self.books:
            filename = f"{book.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            if os.path.exists(filepath):
                downloaded.append(book)
            else:
                missing.append(book)
        
        print(f"Livros já baixados: {len(downloaded)}")
        print(f"Livros faltando: {len(missing)}")
        
        if missing:
            print("\nLivros faltando:")
            for book in missing:
                print(f"  - {book}")
        
        return downloaded, missing

def main():
    """Função principal"""
    downloader = BibleBookDownloader()
    
    # Verificar downloads existentes
    downloaded, missing = downloader.verify_downloads()
    
    if not missing:
        print("OK! Todos os livros já foram baixados!")
        return
    
    # Baixar automaticamente os que faltam
    if missing:
        print(f"\nIniciando download dos {len(missing)} livros faltando...")
        # Baixar todos os livros
        downloader.download_all_books(test_mode=False)
    else:
        print("OK! Todos os livros já foram baixados!")

if __name__ == "__main__":
    main()
