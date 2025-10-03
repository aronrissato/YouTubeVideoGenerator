"""
Criador de vídeo final combinando áudio e vídeos do Pexels
"""
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.video.fx import resize
import tempfile

class VideoCreator:
    def __init__(self):
        self.output_dir = 'output'
        self.temp_dir = 'temp'
        
        # Criar diretórios se não existirem
        for directory in [self.output_dir, self.temp_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
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
                    # Redimensionar para HD (1280x720)
                    clip = clip.resize(height=720)
                    video_clips.append(clip)
                else:
                    print(f"Vídeo não encontrado: {video_file}")
            
            if not video_clips:
                print("Nenhum vídeo válido encontrado")
                return None
            
            print("Concatenando vídeos...")
            # Concatenar todos os vídeos
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Se o vídeo for mais longo que o áudio, cortar
            if final_video.duration > audio_duration:
                final_video = final_video.subclip(0, audio_duration)
            
            # Se o vídeo for mais curto que o áudio, repetir o último frame
            elif final_video.duration < audio_duration:
                # Criar um vídeo estendido repetindo o último frame
                last_frame = final_video.subclip(final_video.duration - 1, final_video.duration)
                extended_clips = [final_video]
                
                # Calcular quantas repetições são necessárias
                remaining_time = audio_duration - final_video.duration
                repetitions = int(remaining_time) + 1
                
                for _ in range(repetitions):
                    extended_clips.append(last_frame)
                
                final_video = concatenate_videoclips(extended_clips, method="compose")
                final_video = final_video.subclip(0, audio_duration)
            
            print("Adicionando áudio ao vídeo...")
            # Adicionar áudio ao vídeo
            final_video = final_video.set_audio(audio_clip)
            
            # Salvar vídeo final
            output_path = os.path.join(self.output_dir, f"{output_filename}.mp4")
            print(f"Renderizando vídeo final: {output_path}")
            
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=24
            )
            
            # Fechar clipes para liberar memória
            audio_clip.close()
            final_video.close()
            for clip in video_clips:
                clip.close()
            
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
