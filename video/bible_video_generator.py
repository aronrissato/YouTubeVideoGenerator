"""
Gerador principal de vídeos bíblicos
Orquestra todo o processo: texto -> áudio -> vídeos -> vídeo final -> publicação
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
from .youtube_publisher import YouTubePublisher
from config.config import video_config, AUDIO_LANGUAGE, AUDIO_SPEED, VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR, TEMP_DIR, PEXELS_VIDEOS_DIR, OUTPUT_DIR, DEFAULT_PRIVACY_STATUS, DEFAULT_CATEGORY_ID

class BibleVideoGenerator:
    def __init__(self, language: Optional[str] = None):
        """
        Inicializa o gerador de vídeos bíblicos
        
        Args:
            language: Código do idioma (ex: 'en', 'pt', 'es'). Se None, usa configuração padrão.
        """
        # Determinar idioma a usar
        self.language = language or video_config.get('language', AUDIO_LANGUAGE)
        
        # Inicializar geradores com idioma específico
        self.text_generator = BibleTextGenerator(language=self.language)
        
        # Usar configurações personalizadas para áudio
        speed = video_config.get('voice_speed', AUDIO_SPEED)
        self.audio_generator = AudioGenerator(self.language, speed)
        
        self.video_fetcher = None  # Será inicializado quando necessário
        self.video_creator = VideoCreator()
        self.youtube_publisher = YouTubePublisher()
        
        # Criar diretórios necessários
        self._create_directories()
        
        print(f"[INFO] BibleVideoGenerator inicializado para idioma: {self.language}")
    
    def _create_directories(self):
        """Cria diretórios necessários para o projeto"""
        directories = [OUTPUT_DIR, VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR, TEMP_DIR, PEXELS_VIDEOS_DIR]
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
                os.path.join(VIDEO_OUTPUT_DIR, f"{book_name}_final.mp4"),
                os.path.join(TEMP_DIR, 'background_music.mp3'),
            ]
            
            # Limpar TODOS os arquivos de áudio gerados (não apenas o do livro atual)
            all_audio_files = glob.glob(os.path.join(AUDIO_OUTPUT_DIR, '*_audio.mp3'))
            temp_files_to_clean.extend(all_audio_files)
            
            # Limpar arquivos de áudio temporários (MoviePy)
            temp_audio_files = glob.glob(os.path.join(TEMP_DIR, 'temp-audio*'))
            temp_files_to_clean.extend(temp_audio_files)
            
            # Limpar arquivos temporários de partes de áudio
            temp_part_audio_files = glob.glob(os.path.join(AUDIO_OUTPUT_DIR, 'temp_part_*.mp3'))
            temp_files_to_clean.extend(temp_part_audio_files)
            
            # Limpar qualquer arquivo temporário de áudio
            temp_audio_output_files = glob.glob(os.path.join(AUDIO_OUTPUT_DIR, '*temp*.mp3'))
            temp_files_to_clean.extend(temp_audio_output_files)
            
            # Limpar arquivos temporários do MoviePy no diretório raiz
            moviepy_temp_files = glob.glob('*TEMP*.mp4')
            temp_files_to_clean.extend(moviepy_temp_files)
            
            # Limpar arquivos temporários do MoviePy no diretório temp
            moviepy_temp_files_temp = glob.glob(os.path.join(TEMP_DIR, '*TEMP*.mp4'))
            temp_files_to_clean.extend(moviepy_temp_files_temp)
            
            # Limpar arquivos temp-audio.m4a que podem ficar no diretório raiz
            temp_audio_root = glob.glob('temp-audio.*')
            temp_files_to_clean.extend(temp_audio_root)
            
            # Limpar vídeos do Pexels baixados
            pexels_videos = glob.glob(os.path.join(PEXELS_VIDEOS_DIR, '*.mp4'))
            temp_files_to_clean.extend(pexels_videos)
            
            # Remover cada arquivo com retry para arquivos bloqueados
            cleaned_count = 0
            for file_path in temp_files_to_clean:
                if os.path.exists(file_path):
                    success = self._remove_file_with_retry(file_path)
                    if success:
                        cleaned_count += 1
            
            # Limpar diretórios vazios
            temp_dirs = [PEXELS_VIDEOS_DIR, TEMP_DIR, AUDIO_OUTPUT_DIR, VIDEO_OUTPUT_DIR]
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
            
            # Etapa 5: Publicar no YouTube (opcional)
            if publish_to_youtube:
                print(f"\nEtapa 5: Publicando no YouTube...")
                
                # Usar configurações personalizadas do YouTube
                youtube_settings = video_config.get('youtube_settings', {})
                privacy = youtube_settings.get('privacy', DEFAULT_PRIVACY_STATUS)
                category = youtube_settings.get('category', DEFAULT_CATEGORY_ID)
                
                # Personalizar título baseado no assunto configurado
                subject_options = video_config.get_subject_options()
                subject_type = video_config.get('subject', 'livro-biblico')
                language = video_config.get('language', 'pt')
                
                # Mapeamento de descrições por idioma
                descriptions = self._get_descriptions_by_language(language)
                
                if subject_type == 'livro-biblico':
                    title = descriptions['livro-biblico']['title'].format(book_name=book_name.upper())
                    description = descriptions['livro-biblico']['description'].format(book_name=book_name.upper())
                elif subject_type == 'salmos':
                    title = descriptions['salmos']['title'].format(book_name=book_name.upper())
                    description = descriptions['salmos']['description'].format(book_name=book_name.upper())
                else:
                    subject_name = subject_options.get(subject_type, 'Conteúdo Bíblico')
                    title = descriptions['outros']['title'].format(subject_name=subject_name, book_name=book_name.upper())
                    description = descriptions['outros']['description'].format(book_name=book_name.upper())
                
                tags = self._get_tags_by_language(language, book_name, subject_type)
                
                video_id = self.youtube_publisher.upload_video(
                    final_video, title, description, tags, category, privacy
                )
                
                if video_id:
                    print(f"Vídeo publicado no YouTube: https://www.youtube.com/watch?v={video_id}")
            
            print("\n" + "=" * 60)
            print("PROCESSO CONCLUÍDO COM SUCESSO!")
            print(f"Arquivos gerados:")
            print(f"   - Texto: {text_file}")
            print(f"   - Áudio: {audio_file}")
            print(f"   - Vídeo: {final_video}")
            
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
        """Lista todos os livros bíblicos disponíveis com número de capítulos e duração estimada"""
        books = self.text_generator.get_available_books()
        
        print("Livros bíblicos disponíveis:")
        print("-" * 80)
        print(f"{'#':<3} {'Livro':<20} {'Capítulos':<10} {'Duração Est.':<15} {'Status':<10}")
        print("-" * 80)
        
        for i, book in enumerate(books, 1):
            book_name = book.replace('-', ' ').title()
            
            # Obter metadados do livro (incluindo duração pré-calculada)
            metadata = self.text_generator.get_book_metadata(book)
            chapters = metadata.get('chapter_count', '?')
            duration_info = metadata.get('duration', {})
            duration_text = duration_info.get('duration_text', 'N/A')
            status = duration_info.get('status', 'N/A')
            
            print(f"{i:<3} {book_name:<20} {chapters:<10} {duration_text:<15} {status:<10}")
        
        print("-" * 80)
        print("Legenda: Curto(<5min) | Médio(5-30min) | Longo(30-60min) | Muito Longo(>60min)")
        
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
                os.path.join(TEMP_DIR, "temp-audio*"),
                os.path.join(PEXELS_VIDEOS_DIR, "*.mp4"),
                os.path.join(TEMP_DIR, 'background_music.mp3'),
                "*TEMP*.mp4",  # Arquivos temporários do MoviePy no diretório raiz
                os.path.join(TEMP_DIR, "*TEMP*.mp4"),  # Arquivos temporários do MoviePy no temp
                "temp-audio.*",  # Arquivos temp-audio que podem ficar no diretório raiz
                os.path.join(AUDIO_OUTPUT_DIR, "temp_part_*.mp3"),  # Arquivos temporários de partes de áudio
                os.path.join(AUDIO_OUTPUT_DIR, "*temp*.mp3"),  # Qualquer arquivo temporário de áudio
            ]
            
            cleaned_count = 0
            for pattern in temp_patterns:
                files = glob.glob(pattern)
                for file_path in files:
                    success = self._remove_file_with_retry(file_path)
                    if success:
                        cleaned_count += 1
            
            # Limpar diretórios vazios após remoção dos arquivos
            temp_dirs = [PEXELS_VIDEOS_DIR, TEMP_DIR, AUDIO_OUTPUT_DIR, VIDEO_OUTPUT_DIR]
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
    
    def _get_descriptions_by_language(self, language: str) -> dict:
        """Retorna descrições e títulos traduzidos baseados no idioma configurado"""
        
        descriptions = {
            'pt': {
                'livro-biblico': {
                    'title': "Livro de {book_name} - Narração Completa da Bíblia",
                    'description': """Narração completa do livro de {book_name} da Bíblia Sagrada.

Este vídeo contém a leitura integral do livro, proporcionando uma experiência de meditação e estudo bíblico.

Que esta palavra abençoe sua vida!

#Bíblia #Cristianismo #Fé #Deus #Jesus #Religião #Meditação #EstudoBíblico #PalavraDeDeus #Espiritualidade"""
                },
                'salmos': {
                    'title': "Salmos de {book_name} - Louvores e Adoração",
                    'description': """Salmos selecionados do livro de {book_name} para meditação e adoração.

Que estes louvores elevem seu coração ao Senhor!

#Salmos #Louvores #Adoração #Bíblia #Cristianismo #Música #Espiritualidade"""
                },
                'outros': {
                    'title': "{subject_name} - {book_name}",
                    'description': """Conteúdo bíblico do livro de {book_name}.

Que a palavra de Deus abençoe sua vida!

#Bíblia #Cristianismo #Fé #PalavraDeDeus #Espiritualidade"""
                }
            },
            'en': {
                'livro-biblico': {
                    'title': "{book_name} | Full Audio Bible",
                    'description': """Complete narration of the book of {book_name} from the Holy Bible.

This video contains the complete reading of the book, providing a meditation and Bible study experience.

May this word bless your life!

#Bible #Christianity #Faith #God #Jesus #Religion #Meditation #BibleStudy #WordOfGod #Spirituality"""
                },
                'salmos': {
                    'title': "Psalms of {book_name} - Praise and Worship",
                    'description': """Selected Psalms from the book of {book_name} for meditation and worship.

May these praises lift your heart to the Lord!

#Psalms #Praise #Worship #Bible #Christianity #Music #Spirituality"""
                },
                'outros': {
                    'title': "{subject_name} - {book_name}",
                    'description': """Biblical content from the book of {book_name}.

May the word of God bless your life!

#Bible #Christianity #Faith #WordOfGod #Spirituality"""
                }
            },
            'es': {
                'livro-biblico': {
                    'title': "Libro de {book_name} - Narración Completa de la Biblia",
                    'description': """Narración completa del libro de {book_name} de la Sagrada Biblia.

Este video contiene la lectura integral del libro, proporcionando una experiencia de meditación y estudio bíblico.

¡Que esta palabra bendiga tu vida!

#Biblia #Cristianismo #Fe #Dios #Jesús #Religión #Meditación #EstudioBíblico #PalabraDeDios #Espiritualidad"""
                },
                'salmos': {
                    'title': "Salmos de {book_name} - Alabanzas y Adoración",
                    'description': """Salmos seleccionados del libro de {book_name} para meditación y adoración.

¡Que estas alabanzas eleven tu corazón al Señor!

#Salmos #Alabanzas #Adoración #Biblia #Cristianismo #Música #Espiritualidad"""
                },
                'outros': {
                    'title': "{subject_name} - {book_name}",
                    'description': """Contenido bíblico del libro de {book_name}.

¡Que la palabra de Dios bendiga tu vida!

#Biblia #Cristianismo #Fe #PalabraDeDios #Espiritualidad"""
                }
            },
            'fr': {
                'livro-biblico': {
                    'title': "Livre de {book_name} - Narration Complète de la Bible",
                    'description': """Narration complète du livre de {book_name} de la Sainte Bible.

Cette vidéo contient la lecture intégrale du livre, offrant une expérience de méditation et d'étude biblique.

Que cette parole bénisse votre vie !

#Bible #Christianisme #Foi #Dieu #Jésus #Religion #Méditation #ÉtudeBiblique #ParoleDeDieu #Spiritualité"""
                },
                'salmos': {
                    'title': "Psaumes de {book_name} - Louanges et Adoration",
                    'description': """Psaumes sélectionnés du livre de {book_name} pour la méditation et l'adoration.

Que ces louanges élèvent votre cœur vers le Seigneur !

#Psaumes #Louanges #Adoration #Bible #Christianisme #Musique #Spiritualité"""
                },
                'outros': {
                    'title': "{subject_name} - {book_name}",
                    'description': """Contenu biblique du livre de {book_name}.

Que la parole de Dieu bénisse votre vie !

#Bible #Christianisme #Foi #ParoleDeDieu #Spiritualité"""
                }
            }
        }
        
        # Retorna descrições em português como fallback se o idioma não estiver disponível
        return descriptions.get(language, descriptions['pt'])
    
    def _get_tags_by_language(self, language: str, book_name: str, subject_type: str) -> list:
        """Retorna tags traduzidas baseadas no idioma configurado"""
        
        tag_sets = {
            'pt': {
                'base': ["bíblia", "cristianismo", "fé", "deus", "jesus", "religião", 
                        "meditação", "estudo bíblico", "palavra de deus", "espiritualidade",
                        book_name.lower(), "narração", "leitura bíblica"],
                'salmos': ["salmos", "louvores", "adoração", "música", "cantos"]
            },
            'en': {
                'base': ["bible", "christianity", "faith", "god", "jesus", "religion",
                        "meditation", "bible study", "word of god", "spirituality",
                        book_name.lower(), "narration", "bible reading"],
                'salmos': ["psalms", "praise", "worship", "music", "songs"]
            },
            'es': {
                'base': ["biblia", "cristianismo", "fe", "dios", "jesús", "religión",
                        "meditación", "estudio bíblico", "palabra de dios", "espiritualidad",
                        book_name.lower(), "narración", "lectura bíblica"],
                'salmos': ["salmos", "alabanzas", "adoración", "música", "cantos"]
            },
            'fr': {
                'base': ["bible", "christianisme", "foi", "dieu", "jésus", "religion",
                        "méditation", "étude biblique", "parole de dieu", "spiritualité",
                        book_name.lower(), "narration", "lecture biblique"],
                'salmos': ["psaumes", "louanges", "adoration", "musique", "chants"]
            }
        }
        
        # Obter tags base
        tags = tag_sets.get(language, tag_sets['pt'])['base']
        
        # Adicionar tags específicas para salmos
        if subject_type == 'salmos':
            tags.extend(tag_sets.get(language, tag_sets['pt'])['salmos'])
        
        return tags

def main():
    """Função principal para execução interativa"""
    # Usar idioma da configuração
    from config.config import video_config
    language = video_config.get('language', 'en')
    
    generator = BibleVideoGenerator(language=language)
    
    print("GERADOR DE VIDEOS BIBLICOS")
    print("=" * 40)
    print(f"Idioma configurado: {language}")
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
