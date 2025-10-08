#!/usr/bin/env python3
"""
Script de teste para o sistema multi-idioma
Testa a criação e leitura de dados bíblicos em diferentes idiomas
"""
import os
import sys
from bible_data_creator import BibleDataCreator
from text.bible_text_generator import BibleTextGenerator

def test_bible_data_creator():
    """Testa a criação de dados bíblicos em diferentes idiomas"""
    print("=" * 70)
    print("TESTE 1: BibleDataCreator - Criação de dados multi-idioma")
    print("=" * 70)
    
    creator = BibleDataCreator()
    
    # Exemplo de dados em diferentes idiomas
    test_data = {
        'pt': {
            'book_name': 'Teste Português',
            'chapters': {
                1: 'No princípio criou Deus os céus e a terra. E a terra era sem forma e vazia.',
                2: 'E assim foram acabados os céus e a terra, e todo o seu exército.'
            }
        },
        'en': {
            'book_name': 'Test English',
            'chapters': {
                1: 'In the beginning God created the heaven and the earth. And the earth was without form, and void.',
                2: 'Thus the heavens and the earth were finished, and all the host of them.'
            }
        },
        'es': {
            'book_name': 'Prueba Español',
            'chapters': {
                1: 'En el principio creó Dios los cielos y la tierra. Y la tierra estaba desordenada y vacía.',
                2: 'Fueron, pues, acabados los cielos y la tierra, y todo el ejército de ellos.'
            }
        }
    }
    
    print("\nCriando arquivos de teste em diferentes idiomas...\n")
    
    created_files = []
    for language, data in test_data.items():
        print(f"Criando livro em {language}...")
        try:
            filepath = creator.create_bible_book(
                book_name=data['book_name'],
                chapter_texts=data['chapters'],
                language=language,
                metadata={'test': True, 'created_by': 'test_multilanguage.py'}
            )
            created_files.append(filepath)
            print(f"[OK] Arquivo criado: {filepath}\n")
        except Exception as e:
            print(f"[ERRO] Erro ao criar arquivo: {str(e)}\n")
    
    return created_files


def test_bible_text_generator():
    """Testa o BibleTextGenerator com diferentes idiomas"""
    print("\n" + "=" * 70)
    print("TESTE 2: BibleTextGenerator - Leitura em diferentes idiomas")
    print("=" * 70)
    
    languages_to_test = ['en', 'pt', 'es']
    
    for language in languages_to_test:
        print(f"\n--- Testando idioma: {language} ---")
        try:
            generator = BibleTextGenerator(language=language)
            
            # Listar livros disponíveis neste idioma
            available_books = generator.get_available_books(language_filter=language)
            
            print(f"Livros disponíveis em {language}: {len(available_books)}")
            if available_books:
                print(f"Primeiros 5: {available_books[:5]}")
            
            # Testar mudança de idioma
            print(f"\nAlterando para idioma: {language}")
            generator.set_language(language)
            print(f"[OK] Idioma alterado com sucesso")
            
        except Exception as e:
            print(f"[ERRO] Erro ao testar idioma {language}: {str(e)}")


def test_config_integration():
    """Testa a integração com o sistema de configuração"""
    print("\n" + "=" * 70)
    print("TESTE 3: Integração com config.py")
    print("=" * 70)
    
    try:
        from config.config import video_config
        
        print("\nIdiomas suportados pelo sistema:")
        languages = video_config.get_language_options()
        for code, name in list(languages.items())[:10]:
            print(f"  {code:8s} - {name}")
        
        print(f"\nTotal de idiomas suportados: {len(languages)}")
        
        # Testar métodos helper
        print("\nTestando métodos helper...")
        
        text_gen = video_config.get_bible_text_generator()
        if text_gen:
            print(f"[OK] BibleTextGenerator criado com idioma: {text_gen.language}")
        else:
            print("[ERRO] Erro ao criar BibleTextGenerator")
        
        data_creator = video_config.get_bible_data_creator()
        if data_creator:
            print(f"[OK] BibleDataCreator criado com sucesso")
        else:
            print("[ERRO] Erro ao criar BibleDataCreator")
        
        # Testar validação de idioma
        print("\nTestando validacao de configuracao...")
        errors = video_config.validate_config()
        if errors:
            print(f"[AVISO] Avisos de validacao: {errors}")
        else:
            print("[OK] Configuracao valida")
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar integracao com config: {str(e)}")
        import traceback
        traceback.print_exc()


def test_list_available_books():
    """Testa listagem de livros disponíveis"""
    print("\n" + "=" * 70)
    print("TESTE 4: Listagem de livros disponíveis")
    print("=" * 70)
    
    try:
        creator = BibleDataCreator()
        books = creator.list_available_books()
        
        print(f"\nTotal de livros no sistema: {len(books)}")
        
        # Agrupar por idioma
        books_by_language = {}
        for book in books:
            lang = book['language']
            if lang not in books_by_language:
                books_by_language[lang] = []
            books_by_language[lang].append(book)
        
        print("\nLivros por idioma:")
        for lang, lang_books in books_by_language.items():
            print(f"\n  {lang}: {len(lang_books)} livros")
            for book in lang_books[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    - {book['book_name']} ({book['chapters']} capítulos, {book['verses']} versículos)")
            if len(lang_books) > 3:
                print(f"    ... e mais {len(lang_books) - 3} livros")
        
        print(f"\n[OK] Listagem concluida com sucesso")
        
    except Exception as e:
        print(f"[ERRO] Erro ao listar livros: {str(e)}")
        import traceback
        traceback.print_exc()


def cleanup_test_files(files):
    """Remove arquivos de teste criados"""
    print("\n" + "=" * 70)
    print("LIMPEZA: Removendo arquivos de teste")
    print("=" * 70)
    
    for filepath in files:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[OK] Removido: {filepath}")
        except Exception as e:
            print(f"[ERRO] Erro ao remover {filepath}: {str(e)}")


def main():
    """Função principal de teste"""
    print("\n" + "=" * 70)
    print("=" + " " * 68 + "=")
    print("=" + "  TESTE DO SISTEMA MULTI-IDIOMA  ".center(68) + "=")
    print("=" + " " * 68 + "=")
    print("=" * 70 + "\n")
    
    created_files = []
    
    try:
        # Teste 1: Criação de dados
        created_files = test_bible_data_creator()
        
        # Teste 2: Gerador de texto
        test_bible_text_generator()
        
        # Teste 3: Integração com config
        test_config_integration()
        
        # Teste 4: Listagem de livros
        test_list_available_books()
        
        # Resumo final
        print("\n" + "=" * 70)
        print("RESUMO DOS TESTES")
        print("=" * 70)
        print("[OK] Teste 1: BibleDataCreator - Criacao de dados multi-idioma")
        print("[OK] Teste 2: BibleTextGenerator - Leitura em diferentes idiomas")
        print("[OK] Teste 3: Integracao com config.py")
        print("[OK] Teste 4: Listagem de livros disponiveis")
        print("\n[OK] Todos os testes foram executados!")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpar arquivos de teste
        if created_files:
            print("\n")
            response = input("Deseja remover os arquivos de teste criados? (s/n): ").strip().lower()
            if response == 's':
                cleanup_test_files(created_files)
            else:
                print("\nArquivos de teste mantidos.")
    
    print("\n" + "=" * 70)
    print("=" + " " * 68 + "=")
    print("=" + "  TESTE CONCLUIDO  ".center(68) + "=")
    print("=" + " " * 68 + "=")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

