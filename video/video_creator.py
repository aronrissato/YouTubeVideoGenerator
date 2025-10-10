"""
Criador de vídeo final combinando áudio e vídeos do Pexels
"""
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
from moviepy.video.fx import resize
from moviepy.audio.fx.all import volumex, audio_loop
import tempfile
import yt_dlp
from config.config import video_config


class ProgressLogger:
    """Logger personalizado para MoviePy que mostra progresso apenas de 10% em 10%"""
    
    def __init__(self):
        self.last_percentage = 0
        self.start_time = None
        self.last_message = ""
    
    def __call__(self, get_frame=None, t=None):
        """Callback chamado pelo MoviePy durante o processamento"""
        # MoviePy passa diferentes parâmetros dependendo do contexto
        # Para write_videofile, recebe get_frame e t (tempo atual)
        pass
    
    def bars_callback(self, bar, attr, value, old_value=None):
        """Callback para o sistema de barras de progresso do MoviePy"""
        if bar == 't' and attr == 'index':
            # value é o frame atual, bar.total é o total de frames
            if hasattr(bar, 'total') and bar.total:
                current_frame = value
                total_frames = bar.total
                
                # Calcular porcentagem
                percentage = int((current_frame / total_frames) * 100)
                
                # Inicializar tempo se for a primeira vez
                if self.start_time is None:
                    self.start_time = time.time()
                
                # Mostrar apenas em múltiplos de 10%
                if percentage >= self.last_percentage + 10 and percentage <= 100:
                    self.last_percentage = percentage - (percentage % 10)  # Arredondar para múltiplo de 10
                    
                    elapsed_time = time.time() - self.start_time
                    
                    if percentage > 0 and percentage < 100:
                        # Calcular tempo estimado restante
                        estimated_total_time = (elapsed_time / percentage) * 100
                        remaining_time = estimated_total_time - elapsed_time
                        
                        # Formatar tempo restante
                        remaining_minutes = int(remaining_time // 60)
                        remaining_seconds = int(remaining_time % 60)
                        
                        message = f"Progresso: {self.last_percentage}% - Tempo estimado restante: {remaining_minutes}m{remaining_seconds:02d}s"
                        print(message, flush=True)
                        self.last_message = message
                    elif percentage >= 100:
                        # Concluído
                        total_minutes = int(elapsed_time // 60)
                        total_seconds = int(elapsed_time % 60)
                        message = f"Progresso: 100% - Concluído em {total_minutes}m{total_seconds:02d}s"
                        print(message, flush=True)
                        self.last_message = message

class VideoCreator:
    def __init__(self):
        from config.config import VIDEO_OUTPUT_DIR, TEMP_DIR
        self.output_dir = VIDEO_OUTPUT_DIR
        self.temp_dir = TEMP_DIR
        
        # Caminho para a música de fundo no repositório
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.background_music_file = os.path.join(project_root, 'music', 'background_music.mp3')
        
        # Usar configurações personalizadas
        self.background_music_enabled = video_config.get('background_music', True)
        self.background_music_volume = video_config.get('background_music_volume', 0.1)
        self.voice_volume = video_config.get('voice_volume', 1.0)
        self.video_quality = video_config.get('video_quality', 'high')
        self.video_style = video_config.get('video_style', 'calm')
        
        # Criar diretórios se não existirem
        for directory in [self.output_dir, self.temp_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _get_background_music(self):
        """
        Retorna o caminho para a música de fundo local
        """
        # Verificar se música de fundo está habilitada
        if not self.background_music_enabled:
            return None
        
        # Verificar se o arquivo existe no repositório
        if os.path.exists(self.background_music_file):
            print(f"Usando música de fundo: {self.background_music_file}")
            return self.background_music_file
        else:
            print(f"Aviso: Arquivo de música não encontrado: {self.background_music_file}")
            print("Continuando sem música de fundo...")
            return None
    
    def create_video_with_audio(self, audio_file: str, video_files: list, output_filename: str) -> str:
        """
        Cria vídeo final combinando áudio e vídeos do Pexels
        """
        try:
            print("Carregando áudio...")
            audio_clip = AudioFileClip(audio_file)
            audio_duration = audio_clip.duration
            
            # Aplicar volume da voz se necessário
            if self.voice_volume != 1.0:
                audio_clip = audio_clip.fx(volumex, self.voice_volume)
            
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
            
            # Obter música de fundo do repositório
            background_music_file = self._get_background_music()
            
            # Variável para armazenar o áudio final que será usado
            audio_to_use = audio_clip
            composite_audio_file = None  # Arquivo temporário do áudio composto para fallback
            
            if background_music_file and os.path.exists(background_music_file):
                print("Combinando narração com música de fundo...")
                print(f"Arquivo de música: {background_music_file}")
                # Carregar música de fundo
                background_music = AudioFileClip(background_music_file)
                print(f"Duração da música: {background_music.duration:.2f}s")
                
                # Ajustar duração da música de fundo para corresponder ao áudio
                if background_music.duration < audio_duration:
                    # Repetir a música se for mais curta usando loop
                    background_music = background_music.fx(audio_loop, duration=audio_duration)
                
                # Cortar para a duração exata
                background_music = background_music.subclip(0, audio_duration)
                
                # Reduzir volume da música de fundo baseado na configuração (usando fx como na versão anterior)
                background_music = background_music.fx(volumex, self.background_music_volume)
                
                # Combinar música de fundo + narração (mesma ordem da versão anterior)
                print(f"Volume da música: {self.background_music_volume}")
                print("Criando áudio composto...")
                final_audio = CompositeAudioClip([background_music, audio_clip])
                print(f"Duração do áudio final: {final_audio.duration:.2f}s")
                
                # Salvar áudio composto em arquivo temporário para fallback do ffmpeg
                composite_audio_file = os.path.join(self.temp_dir, 'composite_audio_temp.mp3')
                print(f"Salvando áudio composto em arquivo temporário: {composite_audio_file}")
                try:
                    # Usar write_audiofile com fps definido explicitamente para AudioClip
                    final_audio.write_audiofile(
                        composite_audio_file, 
                        fps=44100,  # Taxa de amostragem padrão para áudio
                        codec='libmp3lame',
                        bitrate='192k',
                        verbose=False, 
                        logger=None
                    )
                    print("Áudio composto salvo com sucesso")
                except Exception as audio_save_error:
                    print(f"Aviso: Erro ao salvar áudio composto: {str(audio_save_error)}")
                    # Se falhar, usar apenas o arquivo de narração original no fallback
                    composite_audio_file = None
                
                # Usar o áudio composto
                audio_to_use = final_audio
                
                # Fechar clipes para liberar memória (mas manter final_audio até depois de renderizar)
                try:
                    background_music.close()
                except:
                    pass  # Ignorar erros de fechamento
            else:
                # Se não conseguir baixar música de fundo, usar apenas narração
                print("Usando apenas narração (música de fundo não disponível)")
            
            # Aplicar o áudio ao vídeo (seja composto ou apenas narração)
            final_video = final_video.set_audio(audio_to_use)
            
            # Salvar vídeo final
            output_path = os.path.join(self.output_dir, f"{output_filename}.mp4")
            print(f"Renderizando vídeo final: {output_path}", flush=True)
            print(f"Duração do vídeo: {final_video.duration:.2f}s", flush=True)
            print(f"Duração do áudio: {audio_to_use.duration:.2f}s", flush=True)
            
            # Configurar FPS baseado no estilo do vídeo
            fps = 30 if self.video_style == 'dynamic' else 24
            print(f"FPS configurado: {fps}", flush=True)
            
            # Configurações mais robustas para evitar erro de subprocess
            try:
                print("Iniciando write_videofile...", flush=True)
                progress_logger = ProgressLogger()
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    fps=fps,
                    verbose=False,
                    logger=progress_logger.bars_callback
                )
                print("write_videofile completado com sucesso!", flush=True)
            except Exception as write_error:
                # Tentar novamente com configurações mais simples
                print(f"Erro na primeira tentativa: {str(write_error)}")
                print("Tentando com configurações alternativas...")
                
                try:
                    progress_logger = ProgressLogger()
                    final_video.write_videofile(
                        output_path,
                        codec='libx264',
                        audio_codec='aac',
                        fps=fps,
                        verbose=False,
                        logger=progress_logger.bars_callback
                    )
                except Exception as second_error:
                    # Última tentativa sem áudio se necessário
                    print(f"Erro na segunda tentativa: {str(second_error)}")
                    print("Tentando sem áudio...")
                    
                    # Criar vídeo sem áudio temporariamente
                    video_without_audio = final_video.without_audio()
                    progress_logger = ProgressLogger()
                    video_without_audio.write_videofile(
                        output_path,
                        codec='libx264',
                        fps=fps,
                        verbose=False,
                        logger=progress_logger.bars_callback
                    )
                    
                    # Adicionar áudio separadamente usando ffmpeg
                    import subprocess
                    import shutil
                    
                    # Verificar se ffmpeg está disponível
                    if shutil.which('ffmpeg'):
                        temp_video = output_path.replace('.mp4', '_temp.mp4')
                        os.rename(output_path, temp_video)
                        
                        # Usar áudio composto se disponível, caso contrário usar narração original
                        audio_to_add = composite_audio_file if composite_audio_file and os.path.exists(composite_audio_file) else audio_file
                        print(f"Adicionando áudio ao vídeo usando ffmpeg: {audio_to_add}")
                        
                        # Comando ffmpeg para adicionar áudio
                        cmd = [
                            'ffmpeg', '-y',
                            '-i', temp_video,
                            '-i', audio_to_add,
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
            
            # Fechar áudio composto se existir (depois da renderização)
            try:
                if 'final_audio' in locals():
                    final_audio.close()
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
            
            # Limpar arquivo de áudio composto temporário se foi criado
            if composite_audio_file and os.path.exists(composite_audio_file):
                try:
                    os.unlink(composite_audio_file)
                except:
                    pass
            
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
            preview.write_videofile(preview_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            
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
