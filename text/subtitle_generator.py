"""
Gerador de legendas para o vídeo
"""
import os
from typing import List, Tuple
from config.config import video_config

class SubtitleGenerator:
    def __init__(self):
        from config.config import SUBTITLES_DIR
        self.output_dir = SUBTITLES_DIR
        
        # Usar configurações personalizadas
        self.subtitle_style = video_config.get('subtitle_style', 'modern')
        
        # Criar diretório se não existir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def text_to_srt(self, text: str, audio_duration: float, filename: str) -> str:
        """
        Converte texto em formato SRT (legendas)
        """
        try:
            # Dividir texto em frases
            sentences = self._split_into_sentences(text)
            
            # Calcular duração por frase
            duration_per_sentence = audio_duration / len(sentences)
            
            srt_content = []
            
            for i, sentence in enumerate(sentences):
                start_time = i * duration_per_sentence
                end_time = (i + 1) * duration_per_sentence
                
                # Formatar tempo no formato SRT (HH:MM:SS,mmm)
                start_formatted = self._format_time(start_time)
                end_formatted = self._format_time(end_time)
                
                # Adicionar entrada SRT
                srt_content.append(f"{i + 1}")
                srt_content.append(f"{start_formatted} --> {end_formatted}")
                srt_content.append(sentence.strip())
                srt_content.append("")  # Linha em branco
            
            # Salvar arquivo SRT
            srt_path = os.path.join(self.output_dir, f"{filename}.srt")
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))
            
            print(f"Legendas salvas em: {srt_path}")
            return srt_path
            
        except Exception as e:
            print(f"Erro ao gerar legendas: {str(e)}")
            return None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Divide texto em frases para legendas
        """
        # Remover quebras de linha e espaços extras
        text = ' '.join(text.split())
        
        # Dividir por pontos, exclamações e interrogações
        import re
        sentences = re.split(r'[.!?]+', text)
        
        # Filtrar frases vazias e muito curtas
        filtered_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignorar frases muito curtas
                filtered_sentences.append(sentence)
        
        return filtered_sentences
    
    def _format_time(self, seconds: float) -> str:
        """
        Formata tempo em formato SRT (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def create_vtt_subtitle(self, text: str, audio_duration: float, filename: str) -> str:
        """
        Cria legendas no formato VTT (WebVTT)
        """
        try:
            sentences = self._split_into_sentences(text)
            duration_per_sentence = audio_duration / len(sentences)
            
            vtt_content = ["WEBVTT", ""]
            
            for i, sentence in enumerate(sentences):
                start_time = i * duration_per_sentence
                end_time = (i + 1) * duration_per_sentence
                
                # Formatar tempo no formato VTT (HH:MM:SS.mmm)
                start_formatted = self._format_vtt_time(start_time)
                end_formatted = self._format_vtt_time(end_time)
                
                vtt_content.append(f"{start_formatted} --> {end_formatted}")
                vtt_content.append(sentence.strip())
                vtt_content.append("")
            
            # Salvar arquivo VTT
            vtt_path = os.path.join(self.output_dir, f"{filename}.vtt")
            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(vtt_content))
            
            print(f"Legendas VTT salvas em: {vtt_path}")
            return vtt_path
            
        except Exception as e:
            print(f"Erro ao gerar legendas VTT: {str(e)}")
            return None
    
    def _format_vtt_time(self, seconds: float) -> str:
        """
        Formata tempo em formato VTT (HH:MM:SS.mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def add_subtitles_to_video(self, video_path: str, subtitle_path: str, output_path: str) -> str:
        """
        Adiciona legendas diretamente ao vídeo (hardcoded)
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            from moviepy.config import check
            
            # Carregar vídeo
            video = VideoFileClip(video_path)
            
            # Ler arquivo de legendas
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Parse das legendas
            subtitle_clips = self._parse_srt_for_moviepy(srt_content, video.size)
            
            # Combinar vídeo com legendas
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # Salvar vídeo com legendas
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24
            )
            
            video.close()
            final_video.close()
            
            print(f"Vídeo com legendas salvo em: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Erro ao adicionar legendas ao vídeo: {str(e)}")
            return None
    
    def _parse_srt_for_moviepy(self, srt_content: str, video_size: Tuple[int, int]) -> List:
        """
        Converte conteúdo SRT em clipes de texto para MoviePy
        """
        from moviepy.editor import TextClip
        
        subtitle_clips = []
        lines = srt_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            if lines[i].strip().isdigit():  # Número da legenda
                i += 1
                if i < len(lines):
                    # Linha de tempo
                    time_line = lines[i]
                    start_time, end_time = self._parse_time_range(time_line)
                    i += 1
                    if i < len(lines):
                        # Texto da legenda
                        text = lines[i]
                        
                        # Criar clip de texto
                        txt_clip = TextClip(
                            text,
                            fontsize=24,
                            color='white',
                            font='Arial-Bold',
                            stroke_color='black',
                            stroke_width=1
                        ).set_position(('center', video_size[1] - 100)).set_duration(end_time - start_time).set_start(start_time)
                        
                        subtitle_clips.append(txt_clip)
            i += 1
        
        return subtitle_clips
    
    def _parse_time_range(self, time_line: str) -> Tuple[float, float]:
        """
        Converte linha de tempo SRT em segundos
        """
        try:
            start_str, end_str = time_line.split(' --> ')
            start_time = self._srt_time_to_seconds(start_str.strip())
            end_time = self._srt_time_to_seconds(end_str.strip())
            return start_time, end_time
        except:
            return 0, 0
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
        """
        Converte string de tempo SRT em segundos
        """
        try:
            time_str = time_str.replace(',', '.')
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0

def main():
    # Exemplo de uso
    generator = SubtitleGenerator()
    
    sample_text = """
    No princípio, Deus criou os céus e a terra. E a terra era sem forma e vazia; 
    e havia trevas sobre a face do abismo; e o Espírito de Deus se movia sobre a face das águas.
    E disse Deus: Haja luz. E houve luz.
    """
    
    audio_duration = 30.0  # 30 segundos
    
    # Gerar legendas SRT
    srt_file = generator.text_to_srt(sample_text, audio_duration, "teste")
    
    # Gerar legendas VTT
    vtt_file = generator.create_vtt_subtitle(sample_text, audio_duration, "teste")

if __name__ == "__main__":
    main()
