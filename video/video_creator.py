"""
Criador de vídeo final combinando áudio e vídeos do Pexels
"""
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
from moviepy.video.fx import resize
import tempfile
import yt_dlp
from config.config import video_config

class VideoCreator:
    def __init__(self):
        self.output_dir = 'output'
        self.temp_dir = 'temp'
        self.background_music_file = os.path.join(self.temp_dir, 'background_music.mp3')
        
        # Usar configurações personalizadas
        self.background_music_enabled = video_config.get('background_music', True)
        self.background_music_volume = video_config.get('background_music_volume', 0.3)
        self.video_quality = video_config.get('video_quality', 'high')
        self.video_style = video_config.get('video_style', 'calm')
        
        # Criar diretórios se não existirem
        for directory in [self.output_dir, self.temp_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _download_background_music(self):
        """
        Baixa música de fundo do YouTube usando yt-dlp
        """
        # Verificar se música de fundo está habilitada
        if not self.background_music_enabled:
            return None
            
        if os.path.exists(self.background_music_file):
            return self.background_music_file
        
        try:
            # URL da música de fundo do YouTube
            music_url = "https://www.youtube.com/watch?v=fg_wh-qqDf0"
            
            # Configurações do yt-dlp
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(self.temp_dir, "background_music.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "quiet": True,  # Sem output desnecessário para performance
            }
            
            print("Baixando música de fundo do YouTube...")
            
            # Criar diretório temp se não existir
            os.makedirs(self.temp_dir, exist_ok=True)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([music_url])
            
            # Procurar o arquivo baixado (pode ter extensão diferente temporariamente)
            downloaded_file = None
            for file in os.listdir(self.temp_dir):
                if file.startswith("background_music") and file.endswith((".mp3", ".m4a", ".webm")):
                    downloaded_file = os.path.join(self.temp_dir, file)
                    break
            
            if downloaded_file and os.path.exists(downloaded_file):
                # Se o arquivo não é mp3, renomear para mp3
                if not downloaded_file.endswith('.mp3'):
                    if os.path.exists(self.background_music_file):
                        os.unlink(self.background_music_file)
                    os.rename(downloaded_file, self.background_music_file)
                
                print(f"Música de fundo baixada: {self.background_music_file}")
                return self.background_music_file
            else:
                print("Aviso: Arquivo de música não encontrado após download")
                return None
                
        except Exception as e:
            print(f"Aviso: Erro ao baixar música de fundo: {str(e)}")
            return None
    
    def create_video_with_audio(self, audio_file: str, video_files: list, output_filename: str) -> str:
        """
        Cria vídeo final combinando áudio e vídeos do Pexels
        """
        try:
            print("Carregando áudio...")
            audio_clip = AudioFileClip(audio_file)
            audio_duration = audio_clip.duration
            
            print("Carregando vídeos...")
            video_clips = []
            
            for video_file in video_files:
                if os.path.exists(video_file):
                    clip = VideoFileClip(video_file)
                    
                    # Redimensionar baseado na qualidade configurada para consistência
                    if self.video_quality == 'low':
                        clip = clip.resize(height=720)  # 720p
                    elif self.video_quality == 'medium':
                        clip = clip.resize(height=1080)  # 1080p
                    else:  # high
                        clip = clip.resize(height=1080)  # 4K seria muito pesado, usar 1080p
                    
                    # Garantir que todos os vídeos tenham o mesmo tamanho para concatenação
                    clip = clip.resize((1920, 1080)) if self.video_quality != 'low' else clip.resize((1280, 720))
                    
                    video_clips.append(clip)
                else:
                    print(f"Vídeo não encontrado: {video_file}")
            
            if not video_clips:
                print("Nenhum vídeo válido encontrado, criando vídeo apenas com áudio...")
                # Criar um vídeo simples com fundo preto
                from moviepy.editor import ColorClip
                final_video = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio_duration)
            else:
                print("Concatenando vídeos em sequência...")
                # Concatenar todos os vídeos em sequência
                final_video = concatenate_videoclips(video_clips, method="compose")
                
                print(f"Duração total dos vídeos concatenados: {final_video.duration:.2f}s")
                print(f"Duração do áudio: {audio_duration:.2f}s")
            
            # Ajustar duração do vídeo para corresponder exatamente ao áudio
            if final_video.duration > audio_duration:
                # Se o vídeo for mais longo que o áudio, cortar no ponto exato
                print(f"Cortando vídeo de {final_video.duration:.2f}s para {audio_duration:.2f}s")
                final_video = final_video.subclip(0, audio_duration)
            
            elif final_video.duration < audio_duration:
                # Se o vídeo for mais curto que o áudio, estender com repetição dos vídeos
                remaining_time = audio_duration - final_video.duration
                print(f"Estendendo vídeo: faltam {remaining_time:.2f}s")
                
                extended_clips = [final_video]
                
                # Repetir sequência de vídeos até atingir a duração necessária
                while remaining_time > 0:
                    # Se ainda precisamos de mais tempo, repetir a sequência
                    if remaining_time >= final_video.duration:
                        # Adicionar a sequência completa novamente
                        for clip in video_clips:
                            extended_clips.append(clip)
                        remaining_time -= final_video.duration
                    else:
                        # Adicionar apenas parte dos vídeos para completar o tempo
                        current_time = 0
                        for clip in video_clips:
                            if current_time >= remaining_time:
                                break
                            clip_duration = min(clip.duration, remaining_time - current_time)
                            if clip_duration > 0:
                                extended_clips.append(clip.subclip(0, clip_duration))
                                current_time += clip_duration
                        remaining_time = 0
                
                # Concatenar todos os clips estendidos
                final_video = concatenate_videoclips(extended_clips, method="compose")
                final_video = final_video.subclip(0, audio_duration)
            
            print("Adicionando áudio ao vídeo...")
            
            # Baixar música de fundo
            background_music_file = self._download_background_music()
            
            if background_music_file and os.path.exists(background_music_file):
                print("Combinando narração com música de fundo...")
                # Carregar música de fundo
                background_music = AudioFileClip(background_music_file)
                
                # Ajustar duração da música de fundo para corresponder ao áudio
                if background_music.duration < audio_duration:
                    # Repetir a música se for mais curta
                    loops_needed = int(audio_duration / background_music.duration) + 1
                    background_music = concatenate_videoclips([background_music] * loops_needed)
                
                # Cortar para a duração exata
                background_music = background_music.subclip(0, audio_duration)
                
                # Reduzir volume da música de fundo baseado na configuração
                background_music = background_music.volumex(self.background_music_volume)
                
                # Combinar narração + música de fundo
                final_audio = CompositeAudioClip([audio_clip, background_music])
                final_video = final_video.set_audio(final_audio)
                
                # Fechar clipe da música de fundo
                background_music.close()
            else:
                # Se não conseguir baixar música de fundo, usar apenas narração
                print("Usando apenas narração (música de fundo não disponível)")
                final_video = final_video.set_audio(audio_clip)
            
            # Salvar vídeo final
            output_path = os.path.join(self.output_dir, f"{output_filename}.mp4")
            print(f"Renderizando vídeo final: {output_path}")
            
            # Configurar FPS baseado no estilo do vídeo
            fps = 30 if self.video_style == 'dynamic' else 24
            
            # Configurações mais robustas para evitar erro de subprocess
            try:
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    fps=fps,
                    verbose=False,
                    logger=None
                )
            except Exception as write_error:
                # Tentar novamente com configurações mais simples
                print(f"Erro na primeira tentativa: {str(write_error)}")
                print("Tentando com configurações alternativas...")
                
                try:
                    final_video.write_videofile(
                        output_path,
                        codec='libx264',
                        audio_codec='aac',
                        fps=fps,
                        verbose=False,
                        logger=None
                    )
                except Exception as second_error:
                    # Última tentativa sem áudio se necessário
                    print(f"Erro na segunda tentativa: {str(second_error)}")
                    print("Tentando sem áudio...")
                    
                    # Criar vídeo sem áudio temporariamente
                    video_without_audio = final_video.without_audio()
                    video_without_audio.write_videofile(
                        output_path,
                        codec='libx264',
                        fps=fps,
                        verbose=False,
                        logger=None
                    )
                    
                    # Adicionar áudio separadamente usando ffmpeg
                    import subprocess
                    import shutil
                    
                    # Verificar se ffmpeg está disponível
                    if shutil.which('ffmpeg'):
                        temp_video = output_path.replace('.mp4', '_temp.mp4')
                        os.rename(output_path, temp_video)
                        
                        # Comando ffmpeg para adicionar áudio
                        cmd = [
                            'ffmpeg', '-y',
                            '-i', temp_video,
                            '-i', audio_file,
                            '-c:v', 'copy',
                            '-c:a', 'aac',
                            '-map', '0:v:0',
                            '-map', '1:a:0',
                            '-shortest',
                            output_path
                        ]
                        
                        try:
                            subprocess.run(cmd, check=True, capture_output=True)
                            os.remove(temp_video)
                            print("Áudio adicionado com sucesso usando ffmpeg")
                        except subprocess.CalledProcessError as ffmpeg_error:
                            print(f"Erro ao adicionar áudio: {str(ffmpeg_error)}")
                            # Manter vídeo sem áudio
                            os.rename(temp_video, output_path)
                    else:
                        print("ffmpeg não encontrado, mantendo vídeo sem áudio")
            
            # Fechar clipes para liberar memória e evitar bloqueio de arquivos
            try:
                audio_clip.close()
            except:
                pass
            
            try:
                final_video.close()
            except:
                pass
                
            for clip in video_clips:
                try:
                    clip.close()
                except:
                    pass
            
            # Aguardar um pouco para garantir que os recursos sejam liberados
            import time
            time.sleep(0.5)
            
            # Limpar arquivos temporários do MoviePy imediatamente após uso
            self._cleanup_moviepy_temp_files()
            
            print(f"Vídeo criado com sucesso: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Erro ao criar vídeo: {str(e)}")
            return None
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Retorna informações sobre o vídeo
        """
        try:
            clip = VideoFileClip(video_path)
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'audio': clip.audio is not None
            }
            clip.close()
            return info
        except Exception as e:
            print(f"Erro ao obter informações do vídeo: {str(e)}")
            return {}
    
    def _cleanup_moviepy_temp_files(self):
        """
        Remove arquivos temporários do MoviePy imediatamente após uso
        """
        import glob
        try:
            # Limpar arquivos temporários do MoviePy no diretório raiz
            moviepy_temp_files = glob.glob('*TEMP*.mp4')
            for temp_file in moviepy_temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass  # Ignorar erros de limpeza para não interromper o processo
            
            # Limpar arquivos temp-audio que podem ficar no diretório raiz
            temp_audio_files = glob.glob('temp-audio.*')
            for temp_file in temp_audio_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass  # Ignorar erros de limpeza
                    
        except Exception:
            pass  # Ignorar erros para não interromper o processo principal
    
    def create_preview(self, video_path: str, duration: int = 30) -> str:
        """
        Cria uma prévia do vídeo (primeiros X segundos)
        """
        try:
            clip = VideoFileClip(video_path)
            preview = clip.subclip(0, min(duration, clip.duration))
            
            preview_path = os.path.join(self.output_dir, "preview.mp4")
            preview.write_videofile(preview_path, codec='libx264', audio_codec='aac')
            
            clip.close()
            preview.close()
            
            return preview_path
        except Exception as e:
            print(f"Erro ao criar prévia: {str(e)}")
            return None

def main():
    # Exemplo de uso
    creator = VideoCreator()
    
    # Simular criação de vídeo
    audio_file = "audio/teste.mp3"
    video_files = ["pexels_videos/video_1.mp4", "pexels_videos/video_2.mp4"]
    output_filename = "video_final"
    
    if os.path.exists(audio_file):
        result = creator.create_video_with_audio(audio_file, video_files, output_filename)
        if result:
            info = creator.get_video_info(result)
            print(f"Informações do vídeo: {info}")
    else:
        print("Arquivo de áudio não encontrado")

if __name__ == "__main__":
    main()
