"""
Gerador principal de vídeos bíblicos
Orquestra todo o processo: texto -> áudio -> vídeos -> vídeo final -> legendas -> publicação
"""
import os
import sys
from typing import Optional

# Importar módulos do projeto
from bible_text_generator import BibleTextGenerator
from audio_generator import AudioGenerator
from pexels_video_fetcher import PexelsVideoFetcher
from video_creator import VideoCreator
from subtitle_generator import SubtitleGenerator
from youtube_publisher import YouTubePublisher
from config import *

class BibleVideoGenerator:
    def __init__(self):
        self.text_generator = BibleTextGenerator()
        self.audio_generator = AudioGenerator(AUDIO_LANGUAGE, AUDIO_SPEED)
        self.video_fetcher = None  # Será inicializado quando necessário
        self.video_creator = VideoCreator()
        self.subtitle_generator = SubtitleGenerator()
        self.youtube_publisher = YouTubePublisher()
        
        # Criar diretórios necessários
        self._create_directories()
    
    def _create_directories(self):
        """Cria diretórios necessários para o projeto"""
        directories = [VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR, TEMP_DIR, 'pexels_videos', 'subtitles']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def generate_full_video(self, book_name: str, pexels_api_key: str = None, 
                           publish_to_youtube: bool = False) -> Optional[str]:
        """
        Gera vídeo completo de um livro bíblico
        """
        try:
            print(f"🚀 Iniciando geração do vídeo do livro: {book_name.upper()}")
            print("=" * 60)
            
            # Etapa 1: Gerar texto do livro
            print("📖 Etapa 1: Gerando texto do livro...")
            book_text = self.text_generator.get_full_book_text(book_name)
            
            if not book_text:
                print(f"❌ Erro: Não foi possível obter o texto do livro {book_name}")
                return None
            
            print(f"✅ Texto gerado: {len(book_text)} caracteres")
            
            # Salvar texto em arquivo
            text_file = os.path.join(TEMP_DIR, f"{book_name}_text.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(book_text)
            
            # Etapa 2: Gerar áudio
            print("\n🎵 Etapa 2: Gerando narração em áudio...")
            audio_file = self.audio_generator.text_to_speech(book_text, f"{book_name}_audio")
            
            if not audio_file:
                print("❌ Erro: Não foi possível gerar o áudio")
                return None
            
            audio_duration = self.audio_generator.get_audio_duration(audio_file)
            print(f"✅ Áudio gerado: {audio_duration:.2f} segundos")
            
            # Etapa 3: Buscar vídeos do Pexels
            if pexels_api_key:
                print(f"\n🎬 Etapa 3: Buscando vídeos no Pexels...")
                self.video_fetcher = PexelsVideoFetcher(pexels_api_key)
                
                # Obter queries relacionadas ao livro
                queries = self.video_fetcher.get_bible_related_queries(book_name)
                query = queries[0]  # Usar primeira query
                
                video_files = self.video_fetcher.get_videos_for_duration(query, int(audio_duration))
                
                if not video_files:
                    print("⚠️ Nenhum vídeo encontrado no Pexels, usando vídeos de exemplo")
                    video_files = self._get_example_videos()
            else:
                print("⚠️ API key do Pexels não fornecida, usando vídeos de exemplo")
                video_files = self._get_example_videos()
            
            print(f"✅ {len(video_files)} vídeos obtidos")
            
            # Etapa 4: Criar vídeo final
            print(f"\n🎥 Etapa 4: Criando vídeo final...")
            final_video = self.video_creator.create_video_with_audio(
                audio_file, video_files, f"{book_name}_final"
            )
            
            if not final_video:
                print("❌ Erro: Não foi possível criar o vídeo final")
                return None
            
            print(f"✅ Vídeo final criado: {final_video}")
            
            # Etapa 5: Gerar legendas
            print(f"\n📝 Etapa 5: Gerando legendas...")
            subtitle_file = self.subtitle_generator.text_to_srt(
                book_text, audio_duration, f"{book_name}_subtitles"
            )
            
            if subtitle_file:
                print(f"✅ Legendas geradas: {subtitle_file}")
            
            # Etapa 6: Publicar no YouTube (opcional)
            if publish_to_youtube:
                print(f"\n📺 Etapa 6: Publicando no YouTube...")
                title = f"Livro de {book_name.upper()} - Narração Completa da Bíblia"
                description = f"""Narração completa do livro de {book_name.upper()} da Bíblia Sagrada.

📖 Este vídeo contém a leitura integral do livro, proporcionando uma experiência de meditação e estudo bíblico.

🙏 Que esta palavra abençoe sua vida!

#Bíblia #Cristianismo #Fé #Deus #Jesus #Religião #Meditação #EstudoBíblico #PalavraDeDeus #Espiritualidade"""
                
                tags = [
                    "bíblia", "cristianismo", "fé", "deus", "jesus", "religião",
                    "meditação", "estudo bíblico", "palavra de deus", "espiritualidade",
                    book_name.lower(), "narração", "leitura bíblica"
                ]
                
                video_id = self.youtube_publisher.upload_video(
                    final_video, title, description, tags, DEFAULT_CATEGORY_ID, DEFAULT_PRIVACY_STATUS
                )
                
                if video_id and subtitle_file:
                    self.youtube_publisher.upload_subtitle(video_id, subtitle_file)
                    print(f"✅ Vídeo publicado no YouTube: https://www.youtube.com/watch?v={video_id}")
            
            print("\n" + "=" * 60)
            print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
            print(f"📁 Arquivos gerados:")
            print(f"   - Texto: {text_file}")
            print(f"   - Áudio: {audio_file}")
            print(f"   - Vídeo: {final_video}")
            if subtitle_file:
                print(f"   - Legendas: {subtitle_file}")
            
            return final_video
            
        except Exception as e:
            print(f"❌ Erro durante a geração: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_example_videos(self) -> list:
        """
        Retorna lista de vídeos de exemplo (para quando não há API do Pexels)
        """
        # Esta função pode ser expandida para incluir vídeos de exemplo
        # Por enquanto, retorna lista vazia para o processo continuar sem vídeos
        return []
    
    def list_available_books(self):
        """Lista todos os livros bíblicos disponíveis"""
        books = self.text_generator.get_available_books()
        print("📚 Livros bíblicos disponíveis:")
        print("-" * 40)
        
        for i, book in enumerate(books, 1):
            print(f"{i:2d}. {book.replace('-', ' ').title()}")
        
        return books

def main():
    """Função principal para execução interativa"""
    generator = BibleVideoGenerator()
    
    print("🎬 GERADOR DE VÍDEOS BÍBLICOS")
    print("=" * 40)
    
    # Listar livros disponíveis
    books = generator.list_available_books()
    
    print("\n" + "=" * 40)
    
    # Seleção do livro
    while True:
        choice = input("\n📖 Digite o número do livro ou o nome: ").strip()
        
        if choice.isdigit():
            try:
                book_name = books[int(choice) - 1]
                break
            except (ValueError, IndexError):
                print("❌ Número inválido. Tente novamente.")
        else:
            book_name = choice.lower().replace(' ', '-')
            if book_name in books:
                break
            else:
                print(f"❌ Livro '{book_name}' não encontrado. Tente novamente.")
    
    print(f"\n✅ Livro selecionado: {book_name.upper()}")
    
    # Configurações opcionais
    print("\n" + "-" * 40)
    pexels_key = input("🔑 API Key do Pexels (opcional, pressione Enter para pular): ").strip()
    if not pexels_key:
        pexels_key = None
    
    publish = input("📺 Publicar no YouTube? (s/n): ").strip().lower() == 's'
    
    # Gerar vídeo
    print(f"\n🚀 Iniciando geração do vídeo...")
    result = generator.generate_full_video(book_name, pexels_key, publish)
    
    if result:
        print(f"\n🎉 Sucesso! Vídeo gerado: {result}")
    else:
        print(f"\n❌ Falha na geração do vídeo.")

if __name__ == "__main__":
    main()
