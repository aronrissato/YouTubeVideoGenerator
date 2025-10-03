#!/usr/bin/env python3
"""
Script de execução principal simplificado
"""
import sys
import os

def main():
    """Executa o gerador de vídeos bíblicos"""
    try:
        from bible_video_generator import BibleVideoGenerator
        
        print("🎬 GERADOR DE VÍDEOS BÍBLICOS")
        print("=" * 50)
        
        generator = BibleVideoGenerator()
        
        # Verificar se é execução com argumentos
        if len(sys.argv) > 1:
            book_name = sys.argv[1].lower().replace(' ', '-')
            
            # Verificar se livro existe
            available_books = generator.text_generator.get_available_books()
            if book_name not in available_books:
                print(f"❌ Livro '{book_name}' não encontrado.")
                print("📚 Livros disponíveis:")
                for book in available_books[:10]:  # Mostrar apenas os primeiros 10
                    print(f"   - {book}")
                print("   ... (use 'python run.py' para ver todos)")
                return
            
            # Configurações básicas
            print(f"📖 Gerando vídeo para: {book_name.upper()}")
            
            # Verificar variáveis de ambiente
            pexels_key = os.getenv('PEXELS_API_KEY')
            if not pexels_key:
                print("⚠️ PEXELS_API_KEY não configurada. Vídeos não serão baixados.")
            
            publish = input("📺 Publicar no YouTube? (s/n): ").strip().lower() == 's'
            
            # Gerar vídeo
            result = generator.generate_full_video(book_name, pexels_key, publish)
            
            if result:
                print(f"\n🎉 Sucesso! Vídeo: {result}")
            else:
                print("\n❌ Falha na geração do vídeo.")
        else:
            # Execução interativa completa
            generator.list_available_books()
            
            print("\n" + "=" * 50)
            
            # Seleção do livro
            while True:
                choice = input("\n📖 Digite o número do livro ou o nome: ").strip()
                
                if choice.isdigit():
                    try:
                        books = generator.text_generator.get_available_books()
                        book_name = books[int(choice) - 1]
                        break
                    except (ValueError, IndexError):
                        print("❌ Número inválido. Tente novamente.")
                else:
                    book_name = choice.lower().replace(' ', '-')
                    books = generator.text_generator.get_available_books()
                    if book_name in books:
                        break
                    else:
                        print(f"❌ Livro '{book_name}' não encontrado. Tente novamente.")
            
            print(f"\n✅ Livro selecionado: {book_name.upper()}")
            
            # Configurações opcionais
            print("\n" + "-" * 50)
            pexels_key = input("🔑 API Key do Pexels (opcional, pressione Enter para pular): ").strip()
            if not pexels_key:
                pexels_key = os.getenv('PEXELS_API_KEY')
            
            publish = input("📺 Publicar no YouTube? (s/n): ").strip().lower() == 's'
            
            # Gerar vídeo
            print(f"\n🚀 Iniciando geração do vídeo...")
            result = generator.generate_full_video(book_name, pexels_key, publish)
            
            if result:
                print(f"\n🎉 Sucesso! Vídeo: {result}")
            else:
                print(f"\n❌ Falha na geração do vídeo.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Processo interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
