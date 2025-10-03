"""
Gerador principal de vídeos bíblicos
Orquestra todo o processo: texto -> áudio -> vídeos -> vídeo final -> legendas -> publicação
"""
import os
import sys
import shutil
import glob
from typing import Optional

# Importar módulos do projeto
from text.bible_text_generator import BibleTextGenerator
from audio.audio_generator import AudioGenerator
from .pexels_video_fetcher import PexelsVideoFetcher
from .video_creator import VideoCreator
from text.subtitle_generator import SubtitleGenerator
from .youtube_publisher import YouTubePublisher
from config.config import video_config, AUDIO_LANGUAGE, AUDIO_SPEED, VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR, TEMP_DIR, DEFAULT_PRIVACY_STATUS, DEFAULT_CATEGORY_ID

class BibleVideoGenerator:
    def __init__(self):
        self.text_generator = BibleTextGenerator()
        
        # Usar configurações personalizadas para áudio
        language = video_config.get('language', AUDIO_LANGUAGE)
        speed = video_config.get('voice_speed', AUDIO_SPEED)
        self.audio_generator = AudioGenerator(language, speed)
        
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
    
    def _remove_file_with_retry(self, file_path: str, max_retries: int = 3) -> bool:
        """
        Remove arquivo com retry para lidar com arquivos bloqueados
        """
        import time
        
        for attempt in range(max_retries):
            try:
                os.remove(file_path)
                return True
            except (PermissionError, OSError) as e:
                if attempt < max_retries - 1:
                    # Aguardar um pouco antes de tentar novamente
                    time.sleep(1)
                    continue
                else:
                    print(f"Aviso: Não foi possível remover {file_path}: {str(e)}")
                    return False
            except Exception as e:
                print(f"Aviso: Erro inesperado ao remover {file_path}: {str(e)}")
                return False
        
        return False
    
    def _cleanup_temp_files(self, book_name: str):
        """
        Remove arquivos temporários após publicação ou erro
        """
        try:
            # Lista de arquivos temporários para limpar
            temp_files_to_clean = [
                os.path.join(TEMP_DIR, f"{book_name}_text.txt"),
                os.path.join(AUDIO_OUTPUT_DIR, f"{book_name}_audio.mp3"),
                os.path.join(VIDEO_OUTPUT_DIR, f"{book_name}_final.mp4"),
                os.path.join('subtitles', f"{book_name}_subtitles.srt"),
                os.path.join('temp', 'background_music.mp3'),
            ]
            
            # Limpar arquivos de áudio temporários (MoviePy)
            temp_audio_files = glob.glob(os.path.join('temp', 'temp-audio*'))
            temp_files_to_clean.extend(temp_audio_files)
            
            # Limpar arquivos temporários do MoviePy no diretório raiz
            moviepy_temp_files = glob.glob('*TEMP*.mp4')
            temp_files_to_clean.extend(moviepy_temp_files)
            
            # Limpar arquivos temporários do MoviePy no diretório temp
            moviepy_temp_files_temp = glob.glob(os.path.join('temp', '*TEMP*.mp4'))
            temp_files_to_clean.extend(moviepy_temp_files_temp)
            
            # Limpar arquivos temp-audio.m4a que podem ficar no diretório raiz
            temp_audio_root = glob.glob('temp-audio.*')
            temp_files_to_clean.extend(temp_audio_root)
            
            # Limpar vídeos do Pexels baixados
            pexels_videos = glob.glob(os.path.join('pexels_videos', '*.mp4'))
            temp_files_to_clean.extend(pexels_videos)
            
            # Remover cada arquivo com retry para arquivos bloqueados
            cleaned_count = 0
            for file_path in temp_files_to_clean:
                if os.path.exists(file_path):
                    success = self._remove_file_with_retry(file_path)
                    if success:
                        cleaned_count += 1
            
            # Limpar diretórios vazios
            temp_dirs = ['pexels_videos', 'temp', 'audio', 'output', 'subtitles']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        # Tentar remover diretório se estiver vazio
                        if not os.listdir(temp_dir):
                            os.rmdir(temp_dir)
                    except Exception:
                        pass  # Ignorar se não conseguir remover o diretório
            
            if cleaned_count > 0:
                print(f"Limpeza concluída: {cleaned_count} arquivos temporários removidos")
            
        except Exception as e:
            print(f"Erro durante limpeza: {str(e)}")
    
    def _cleanup_on_error(self, book_name: str):
        """
        Limpeza específica em caso de erro
        """
        print("Realizando limpeza devido a erro...")
        self._cleanup_temp_files(book_name)
    
    def generate_full_video(self, book_name: str, pexels_api_key: str = None, 
                           publish_to_youtube: bool = False) -> Optional[str]:
        """
        Gera vídeo completo de um livro bíblico
        """
        try:
            print(f"Iniciando geração do vídeo do livro: {book_name.upper()}")
            print("=" * 60)
            
            # Etapa 1: Gerar texto do livro
            print("Etapa 1: Gerando texto do livro...")
            book_text = self.text_generator.get_full_book_text(book_name)
            
            if not book_text:
                print(f"ERRO: Não foi possível obter o texto do livro {book_name}")
                return None
            
            print(f"Texto gerado: {len(book_text)} caracteres")
            
            # Salvar texto em arquivo
            text_file = os.path.join(TEMP_DIR, f"{book_name}_text.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(book_text)
            
            # Etapa 2: Gerar áudio
            print("\nEtapa 2: Gerando narração em áudio...")
            audio_file = self.audio_generator.text_to_speech(book_text, f"{book_name}_audio")
            
            if not audio_file:
                print("ERRO: Não foi possível gerar o áudio")
                return None
            
            audio_duration = self.audio_generator.get_audio_duration(audio_file)
            print(f"Áudio gerado: {audio_duration:.2f} segundos")
            
            # Etapa 3: Buscar vídeos do Pexels (OBRIGATÓRIO)
            if pexels_api_key:
                print(f"\nEtapa 3: Buscando vídeos no Pexels...")
                self.video_fetcher = PexelsVideoFetcher(pexels_api_key)
                
                # Obter queries relacionadas ao livro
                queries = self.video_fetcher.get_bible_related_queries(book_name)
                query = queries[0]  # Usar primeira query
                
                video_files = self.video_fetcher.get_videos_for_duration(query, int(audio_duration))
                
                if not video_files:
                    print("ERRO: Nenhum vídeo encontrado no Pexels")
                    print("O vídeo final deve conter tanto narração quanto imagens")
                    return None
            else:
                print("ERRO: API key do Pexels é obrigatória")
                print("O vídeo final deve conter tanto narração quanto imagens")
                return None
            
            print(f"{len(video_files)} vídeos obtidos")
            
            # Etapa 4: Criar vídeo final
            print(f"\nEtapa 4: Criando vídeo final...")
            final_video = self.video_creator.create_video_with_audio(
                audio_file, video_files, f"{book_name}_final"
            )
            
            if not final_video:
                print("ERRO: Não foi possível criar o vídeo final")
                return None
            
            print(f"Vídeo final criado: {final_video}")
            
            # Etapa 5: Gerar legendas
            print(f"\nEtapa 5: Gerando legendas...")
            subtitle_file = self.subtitle_generator.text_to_srt(
                book_text, audio_duration, f"{book_name}_subtitles"
            )
            
            if subtitle_file:
                print(f"Legendas geradas: {subtitle_file}")
            
            # Etapa 6: Publicar no YouTube (opcional)
            if publish_to_youtube:
                print(f"\nEtapa 6: Publicando no YouTube...")
                
                # Usar configurações personalizadas do YouTube
                youtube_settings = video_config.get('youtube_settings', {})
                privacy = youtube_settings.get('privacy', DEFAULT_PRIVACY_STATUS)
                category = youtube_settings.get('category', DEFAULT_CATEGORY_ID)
                
                # Personalizar título baseado no assunto configurado
                subject_options = video_config.get_subject_options()
                subject_type = video_config.get('subject', 'livro-biblico')
                
                if subject_type == 'livro-biblico':
                    title = f"Livro de {book_name.upper()} - Narração Completa da Bíblia"
                    description = f"""Narração completa do livro de {book_name.upper()} da Bíblia Sagrada.

Este vídeo contém a leitura integral do livro, proporcionando uma experiência de meditação e estudo bíblico.

Que esta palavra abençoe sua vida!

#Bíblia #Cristianismo #Fé #Deus #Jesus #Religião #Meditação #EstudoBíblico #PalavraDeDeus #Espiritualidade"""
                elif subject_type == 'salmos':
                    title = f"Salmos de {book_name.upper()} - Louvores e Adoração"
                    description = f"""Salmos selecionados do livro de {book_name.upper()} para meditação e adoração.

Que estes louvores elevem seu coração ao Senhor!

#Salmos #Louvores #Adoração #Bíblia #Cristianismo #Música #Espiritualidade"""
                else:
                    title = f"{subject_options.get(subject_type, 'Conteúdo Bíblico')} - {book_name.upper()}"
                    description = f"""Conteúdo bíblico do livro de {book_name.upper()}.

Que a palavra de Deus abençoe sua vida!

#Bíblia #Cristianismo #Fé #PalavraDeDeus #Espiritualidade"""
                
                tags = [
                    "bíblia", "cristianismo", "fé", "deus", "jesus", "religião",
                    "meditação", "estudo bíblico", "palavra de deus", "espiritualidade",
                    book_name.lower(), "narração", "leitura bíblica"
                ]
                
                video_id = self.youtube_publisher.upload_video(
                    final_video, title, description, tags, category, privacy
                )
                
                if video_id and subtitle_file:
                    self.youtube_publisher.upload_subtitle(video_id, subtitle_file)
                    print(f"Vídeo publicado no YouTube: https://www.youtube.com/watch?v={video_id}")
            
            print("\n" + "=" * 60)
            print("PROCESSO CONCLUÍDO COM SUCESSO!")
            print(f"Arquivos gerados:")
            print(f"   - Texto: {text_file}")
            print(f"   - Áudio: {audio_file}")
            print(f"   - Vídeo: {final_video}")
            if subtitle_file:
                print(f"   - Legendas: {subtitle_file}")
            
            # Limpeza após sucesso
            if publish_to_youtube:
                print("\nRealizando limpeza após publicação...")
                self._cleanup_temp_files(book_name)
            
            return final_video
            
        except Exception as e:
            print(f"Erro durante a geração: {str(e)}")
            import traceback
            traceback.print_exc()
            # Limpeza em caso de erro
            self._cleanup_on_error(book_name)
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
        print("Livros bíblicos disponíveis:")
        print("-" * 40)
        
        for i, book in enumerate(books, 1):
            print(f"{i:2d}. {book.replace('-', ' ').title()}")
        
        return books
    
    def manual_cleanup(self, book_name: str = None):
        """
        Limpeza manual de arquivos temporários
        """
        if book_name:
            print(f"Limpando arquivos do livro: {book_name}")
            self._cleanup_temp_files(book_name)
        else:
            print("Limpando todos os arquivos temporários...")
            # Limpar todos os arquivos temporários
            temp_patterns = [
                os.path.join(TEMP_DIR, "*_text.txt"),
                os.path.join(AUDIO_OUTPUT_DIR, "*_audio.mp3"),
                os.path.join(VIDEO_OUTPUT_DIR, "*_final.mp4"),
                os.path.join('subtitles', "*_subtitles.srt"),
                os.path.join('temp', "temp-audio*"),
                os.path.join('pexels_videos', "*.mp4"),
                os.path.join('temp', 'background_music.mp3'),
                "*TEMP*.mp4",  # Arquivos temporários do MoviePy no diretório raiz
                os.path.join('temp', "*TEMP*.mp4"),  # Arquivos temporários do MoviePy no temp
                "temp-audio.*",  # Arquivos temp-audio que podem ficar no diretório raiz
            ]
            
            cleaned_count = 0
            for pattern in temp_patterns:
                files = glob.glob(pattern)
                for file_path in files:
                    success = self._remove_file_with_retry(file_path)
                    if success:
                        cleaned_count += 1
            
            # Limpar diretórios vazios após remoção dos arquivos
            temp_dirs = ['pexels_videos', 'temp', 'audio', 'output', 'subtitles']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        # Tentar remover diretório se estiver vazio
                        if not os.listdir(temp_dir):
                            os.rmdir(temp_dir)
                    except Exception:
                        pass  # Ignorar se não conseguir remover o diretório
            
            if cleaned_count > 0:
                print(f"Limpeza completa: {cleaned_count} arquivos temporários removidos")
            else:
                print("Nenhum arquivo temporário encontrado para limpeza")

def main():
    """Função principal para execução interativa"""
    generator = BibleVideoGenerator()
    
    print("GERADOR DE VIDEOS BIBLICOS")
    print("=" * 40)
    
    # Listar livros disponíveis
    books = generator.list_available_books()
    
    print("\n" + "=" * 40)
    
    # Seleção do livro
    while True:
        choice = input("\nDigite o número do livro ou o nome: ").strip()
        
        if choice.isdigit():
            try:
                book_name = books[int(choice) - 1]
                break
            except (ValueError, IndexError):
                print("ERRO: Número inválido. Tente novamente.")
        else:
            book_name = choice.lower().replace(' ', '-')
            if book_name in books:
                break
            else:
                print(f"ERRO: Livro '{book_name}' não encontrado. Tente novamente.")
    
    print(f"\nLivro selecionado: {book_name.upper()}")
    
    # Configurações opcionais
    print("\n" + "-" * 40)
    pexels_key = input("API Key do Pexels (opcional, pressione Enter para pular): ").strip()
    if not pexels_key:
        pexels_key = None
    
    publish = input("Publicar no YouTube? (s/n): ").strip().lower() == 's'
    
    # Gerar vídeo
    print(f"\nIniciando geração do vídeo...")
    result = generator.generate_full_video(book_name, pexels_key, publish)
    
    if result:
        print(f"\nSucesso! Vídeo gerado: {result}")
    else:
        print(f"\nFalha na geração do vídeo.")

if __name__ == "__main__":
    main()
