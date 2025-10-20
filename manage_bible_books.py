#!/usr/bin/env python3
"""
Script para gerenciar livros bíblicos em múltiplos idiomas
"""
import os
import json
import sys

def check_books_status():
    """Verifica status dos livros por idioma"""
    bible_dir = 'bible_data'
    stats = {}
    books_by_lang = {}
    
    for filename in os.listdir(bible_dir):
        if filename.endswith('.json') and not filename.endswith('_backup.json'):
            filepath = os.path.join(bible_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang = data.get('language', 'unknown')
                    
                    if lang not in stats:
                        stats[lang] = 0
                        books_by_lang[lang] = []
                    
                    stats[lang] += 1
                    books_by_lang[lang].append({
                        'file': filename.replace('.json', ''),
                        'name': data.get('reference', 'N/A')
                    })
            except:
                pass
    
    print("=" * 70)
    print("📊 STATUS DOS LIVROS BÍBLICOS")
    print("=" * 70)
    
    for lang, count in sorted(stats.items()):
        lang_name = {
            'pt': '🇧🇷 Português',
            'en': '🇺🇸 Inglês',
            'es': '🇪🇸 Espanhol',
            'unknown': '❓ Desconhecido'
        }.get(lang, f'🌍 {lang.upper()}')
        
        print(f"\n{lang_name}: {count} livros")
        
        # Mostrar primeiros 10 livros
        for book in sorted(books_by_lang[lang], key=lambda x: x['file'])[:10]:
            print(f"   • {book['file']:20s} - {book['name']}")
        
        if count > 10:
            print(f"   ... e mais {count - 10} livros")
    
    print("\n" + "=" * 70)
    print(f"Total: {sum(stats.values())} livros")
    print("=" * 70)

def download_books_menu():
    """Menu para baixar livros"""
    print("\n" + "=" * 70)
    print("📥 BAIXAR LIVROS BÍBLICOS")
    print("=" * 70)
    print("\nIdiomas disponíveis:")
    print("1. Português (Brasil) - pt")
    print("2. [Outros idiomas em desenvolvimento]")
    
    print("\nOpções de download:")
    print("a. Baixar todos os 66 livros em português")
    print("b. Baixar livro específico em português")
    print("c. Baixar livros curtos para teste (6 livros)")
    print("0. Voltar")
    
    choice = input("\nEscolha uma opção: ").strip().lower()
    
    if choice == 'a':
        print("\n⚠ Isso vai baixar 66 livros e pode demorar 15-30 minutos.")
        confirm = input("Confirma? (s/n): ").strip().lower()
        if confirm == 's':
            os.system('python bible_data/download_portuguese_bible_v2.py all')
    
    elif choice == 'b':
        print("\nExemplos: genesis, jonah, matthew, revelation")
        book = input("Digite o nome do livro em inglês: ").strip().lower()
        if book:
            os.system(f'python bible_data/download_portuguese_bible_v2.py {book}')
    
    elif choice == 'c':
        os.system('python bible_data/download_portuguese_bible_v2.py')

def main():
    """Menu principal"""
    while True:
        print("\n" + "=" * 70)
        print("🌍 GERENCIADOR DE LIVROS BÍBLICOS MULTI-IDIOMA")
        print("=" * 70)
        print("\n1. Ver status dos livros")
        print("2. Baixar livros em português")
        print("3. Instruções de uso")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            check_books_status()
        
        elif choice == '2':
            download_books_menu()
        
        elif choice == '3':
            print("\n" + "=" * 70)
            print("📖 INSTRUÇÕES DE USO")
            print("=" * 70)
            print("""
1. BAIXAR LIVROS EM PORTUGUÊS:
   - Use a opção 2 do menu
   - Escolha 'a' para baixar todos ou 'b' para específico
   
2. CONFIGURAR IDIOMA:
   - Edite video_config.json
   - Altere "language" para "pt" ou "pt-BR"
   
3. GERAR VÍDEO:
   - Execute: python run.py
   - Escolha o livro desejado
   - O vídeo será gerado com texto e áudio em português!
   
4. ADICIONAR NOVO IDIOMA:
   - Consulte: bible_data/README_MULTILANGUAGE.md
   
Para mais informações, veja:
- bible_data/README_MULTILANGUAGE.md (guia completo)
- README.md (documentação geral)
            """)
            input("\nPressione Enter para continuar...")
        
        elif choice == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida!")

if __name__ == "__main__":
    main()


