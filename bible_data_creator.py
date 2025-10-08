#!/usr/bin/env python3
"""
Criador de dados para livros da bíblia em qualquer idioma
Sistema genérico que suporta múltiplos idiomas
"""
import os
import json
from typing import Dict, List, Optional

class BibleDataCreator:
    """Classe para criar dados bíblicos em qualquer idioma"""
    
    # Mapeamento de idiomas suportados
    SUPPORTED_LANGUAGES = {
        'pt': 'Português (Brasil)',
        'pt-pt': 'Português (Portugal)',
        'en': 'English (US)',
        'en-gb': 'English (UK)',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'it': 'Italiano',
        'ru': 'Русский',
        'zh': '中文',
        'ja': '日本語',
        'ko': '한국어',
        'ar': 'العربية',
        'he': 'עברית'
    }
    
    def __init__(self, bible_dir: str = "bible_data"):
        """
        Inicializa o criador de dados bíblicos
        
        Args:
            bible_dir: Diretório onde os dados serão salvos
        """
        self.bible_dir = bible_dir
        if not os.path.exists(bible_dir):
            os.makedirs(bible_dir)
    
    def create_bible_book(self, 
                         book_name: str, 
                         chapter_texts: Dict[int, str],
                         language: str = 'en',
                         metadata: Optional[Dict] = None) -> str:
        """
        Cria dados para um livro da bíblia em qualquer idioma
        
        Args:
            book_name: Nome do livro
            chapter_texts: Dicionário {capítulo: texto}
            language: Código do idioma (ex: 'en', 'pt', 'es')
            metadata: Metadados opcionais (duração, autor, etc.)
        
        Returns:
            Caminho do arquivo criado
        """
        # Validar idioma
        if language not in self.SUPPORTED_LANGUAGES:
            print(f"[WARNING] Idioma '{language}' não está na lista de suportados. Continuando mesmo assim...")
        
        # Estrutura do livro
        book_data = {
            "reference": book_name,
            "language": language,
            "language_name": self.SUPPORTED_LANGUAGES.get(language, "Unknown"),
            "verses": [],
            "text": "",
            "metadata": metadata or {}
        }
        
        # Criar versículos para cada capítulo
        for chapter, text in sorted(chapter_texts.items()):
            # Dividir o texto em versículos (aproximadamente)
            # Usa diferentes delimitadores dependendo do idioma
            sentences = self._split_text_into_verses(text, language)
            verse_num = 1
            
            for sentence in sentences:
                if sentence.strip():
                    verse_text = sentence.strip()
                    
                    # Adicionar pontuação final se necessário
                    if not self._has_ending_punctuation(verse_text, language):
                        verse_text += '.'
                    
                    book_data["verses"].append({
                        "chapter": chapter,
                        "verse": verse_num,
                        "text": verse_text
                    })
                    verse_num += 1
        
        # Criar texto completo
        book_data["text"] = " ".join([v["text"] for v in book_data["verses"]])
        
        # Adicionar estatísticas aos metadados
        book_data["metadata"].update({
            "chapter_count": len(chapter_texts),
            "verse_count": len(book_data["verses"]),
            "character_count": len(book_data["text"]),
            "word_count": len(book_data["text"].split())
        })
        
        # Salvar arquivo
        filename = f"{book_name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(self.bible_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] {self.SUPPORTED_LANGUAGES.get(language, language)} {book_name} data created: {filepath}")
        print(f"[INFO] {len(book_data['verses'])} verses in {len(chapter_texts)} chapters")
        print(f"[INFO] {len(book_data['text'])} characters, {book_data['metadata']['word_count']} words")
        
        return filepath
    
    def _split_text_into_verses(self, text: str, language: str) -> List[str]:
        """
        Divide texto em versículos baseado no idioma
        
        Args:
            text: Texto a ser dividido
            language: Código do idioma
        
        Returns:
            Lista de versículos
        """
        # Delimitadores por idioma
        if language in ['zh', 'ja']:
            # Idiomas asiáticos usam pontuação diferente
            return text.split('。')
        elif language == 'ar':
            # Árabe usa ponto diferente
            sentences = text.split('.')
        else:
            # Idiomas ocidentais
            sentences = text.split('. ')
        
        return sentences
    
    def _has_ending_punctuation(self, text: str, language: str) -> bool:
        """
        Verifica se o texto tem pontuação final apropriada
        
        Args:
            text: Texto a verificar
            language: Código do idioma
        
        Returns:
            True se tem pontuação final
        """
        if not text:
            return False
        
        # Pontuações finais por idioma
        if language in ['zh', 'ja']:
            return text[-1] in ['。', '！', '？']
        else:
            return text[-1] in ['.', '!', '?', ':', ';']
    
    def load_bible_book(self, book_name: str) -> Optional[Dict]:
        """
        Carrega dados de um livro do armazenamento local
        
        Args:
            book_name: Nome do livro
        
        Returns:
            Dados do livro ou None se não encontrado
        """
        filename = f"{book_name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(self.bible_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Erro ao carregar arquivo local {filepath}: {str(e)}")
            return None
    
    def list_available_books(self) -> List[Dict[str, str]]:
        """
        Lista todos os livros disponíveis no diretório
        
        Returns:
            Lista de dicionários com informações dos livros
        """
        books = []
        
        if not os.path.exists(self.bible_dir):
            return books
        
        for filename in os.listdir(self.bible_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.bible_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        books.append({
                            'filename': filename,
                            'book_name': data.get('reference', 'Unknown'),
                            'language': data.get('language', 'unknown'),
                            'language_name': data.get('language_name', 'Unknown'),
                            'chapters': data.get('metadata', {}).get('chapter_count', 0),
                            'verses': data.get('metadata', {}).get('verse_count', 0)
                        })
                except Exception as e:
                    print(f"[WARNING] Erro ao ler {filename}: {str(e)}")
        
        return sorted(books, key=lambda x: x['book_name'])
    
    def convert_book_language(self, book_name: str, target_language: str) -> Optional[str]:
        """
        Converte um livro existente para outro idioma
        (Nota: Requer integração com serviço de tradução)
        
        Args:
            book_name: Nome do livro a converter
            target_language: Idioma alvo
        
        Returns:
            Caminho do novo arquivo ou None se falhar
        """
        print(f"[INFO] Conversão de idioma requer integração com API de tradução")
        print(f"[INFO] Funcionalidade planejada para versão futura")
        return None
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """
        Retorna dicionário de idiomas suportados
        
        Returns:
            Dict com código: nome do idioma
        """
        return cls.SUPPORTED_LANGUAGES.copy()


def main():
    """Função principal para demonstrar uso"""
    print("=" * 60)
    print("BIBLE DATA CREATOR - Sistema Multi-Idioma")
    print("=" * 60)
    
    creator = BibleDataCreator()
    
    print("\nIdiomas suportados:")
    for code, name in creator.get_supported_languages().items():
        print(f"  {code:6s} - {name}")
    
    print("\n" + "=" * 60)
    print("Livros disponíveis no sistema:")
    print("=" * 60)
    
    books = creator.list_available_books()
    if books:
        for book in books:
            print(f"\n📖 {book['book_name']}")
            print(f"   Idioma: {book['language_name']} ({book['language']})")
            print(f"   Capítulos: {book['chapters']} | Versículos: {book['verses']}")
            print(f"   Arquivo: {book['filename']}")
    else:
        print("\nNenhum livro encontrado no diretório 'bible_data/'")
    
    print("\n" + "=" * 60)
    print("Exemplo de uso:")
    print("=" * 60)
    print("""
from bible_data_creator import BibleDataCreator

# Criar instância
creator = BibleDataCreator()

# Criar livro em português
chapter_texts = {
    1: 'No princípio criou Deus os céus e a terra. E a terra era sem forma e vazia.',
    2: 'E assim foram acabados os céus e a terra, e todo o seu exército.'
}
creator.create_bible_book('Gênesis', chapter_texts, language='pt')

# Criar livro em espanhol
chapter_texts_es = {
    1: 'En el principio creó Dios los cielos y la tierra. Y la tierra estaba desordenada y vacía.',
    2: 'Fueron, pues, acabados los cielos y la tierra, y todo el ejército de ellos.'
}
creator.create_bible_book('Génesis', chapter_texts_es, language='es')
    """)


if __name__ == "__main__":
    main()

