"""
Gerador de áudio/narração do texto bíblico
"""
import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import tempfile

class AudioGenerator:
    def __init__(self, language='pt', speed=1.0):
        self.language = language
        self.speed = speed
        self.output_dir = 'audio'
        
        # Criar diretório de saída se não existir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def text_to_speech(self, text: str, output_filename: str) -> str:
        """
        Converte texto em fala e retorna o caminho do arquivo de áudio
        """
        try:
            # Dividir texto em partes menores se muito longo
            max_length = 5000  # Limite do gTTS
            text_parts = self._split_text(text, max_length)
            
            audio_segments = []
            
            for i, part in enumerate(text_parts):
                print(f"Gerando áudio parte {i+1}/{len(text_parts)}...")
                
                # Gerar áudio com gTTS
                tts = gTTS(text=part, lang=self.language, slow=False)
                
                # Salvar temporariamente
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts.save(temp_file.name)
                
                # Carregar e processar áudio
                audio = AudioSegment.from_mp3(temp_file.name)
                
                # Aplicar velocidade se necessário
                if self.speed != 1.0:
                    audio = speedup(audio, playback_speed=self.speed)
                
                audio_segments.append(audio)
                
                # Limpar arquivo temporário
                os.unlink(temp_file.name)
            
            # Combinar todos os segmentos
            if len(audio_segments) > 1:
                final_audio = audio_segments[0]
                for segment in audio_segments[1:]:
                    final_audio += segment
            else:
                final_audio = audio_segments[0]
            
            # Salvar arquivo final
            output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
            final_audio.export(output_path, format="mp3")
            
            print(f"Áudio salvo em: {output_path}")
            print(f"Duração do áudio: {len(final_audio) / 1000:.2f} segundos")
            
            return output_path
            
        except Exception as e:
            print(f"Erro ao gerar áudio: {str(e)}")
            return None
    
    def get_audio_duration(self, audio_file_path: str) -> float:
        """
        Retorna a duração do áudio em segundos
        """
        try:
            audio = AudioSegment.from_mp3(audio_file_path)
            return len(audio) / 1000.0
        except Exception as e:
            print(f"Erro ao obter duração do áudio: {str(e)}")
            return 0.0
    
    def _split_text(self, text: str, max_length: int) -> list:
        """
        Divide texto em partes menores respeitando o limite de caracteres
        """
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current_part = ""
        
        # Dividir por parágrafos primeiro
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_part) + len(paragraph) <= max_length:
                current_part += paragraph + '\n\n'
            else:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = paragraph + '\n\n'
                else:
                    # Se um parágrafo é muito longo, dividir por frases
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        if len(current_part) + len(sentence) <= max_length:
                            current_part += sentence + '. '
                        else:
                            if current_part:
                                parts.append(current_part.strip())
                                current_part = sentence + '. '
                            else:
                                # Se uma frase é muito longa, dividir por palavras
                                words = sentence.split()
                                for word in words:
                                    if len(current_part) + len(word) <= max_length:
                                        current_part += word + ' '
                                    else:
                                        if current_part:
                                            parts.append(current_part.strip())
                                            current_part = word + ' '
                                        else:
                                            parts.append(word)
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts

def main():
    # Exemplo de uso
    audio_gen = AudioGenerator()
    
    # Texto de exemplo
    sample_text = """
    No princípio, Deus criou os céus e a terra. E a terra era sem forma e vazia; 
    e havia trevas sobre a face do abismo; e o Espírito de Deus se movia sobre a face das águas.
    E disse Deus: Haja luz. E houve luz.
    """
    
    audio_file = audio_gen.text_to_speech(sample_text, "teste")
    if audio_file:
        duration = audio_gen.get_audio_duration(audio_file)
        print(f"Duração: {duration:.2f} segundos")

if __name__ == "__main__":
    main()
