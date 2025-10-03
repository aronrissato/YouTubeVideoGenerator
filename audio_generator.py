"""
Gerador de áudio/narração do texto bíblico
"""
import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import tempfile
import pyttsx3
from config import video_config

class AudioGenerator:
    def __init__(self, language='en', speed=1.0):
        # Usar configurações personalizadas se disponíveis
        self.language = video_config.get('language', language)
        self.speed = video_config.get('voice_speed', speed)
        self.voice_gender = video_config.get('voice_gender', 'female')
        self.output_dir = 'audio'
        
        # Criar diretório de saída se não existir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def text_to_speech(self, text: str, output_filename: str) -> str:
        """
        Converte texto em fala e retorna o caminho do arquivo de áudio
        """
        import time
        
        try:
            # Dividir texto em partes menores se muito longo
            max_length = 5000  # Limite do gTTS
            text_parts = self._split_text(text, max_length)
            
            audio_segments = []
            
            for i, part in enumerate(text_parts):
                print(f"Gerando áudio parte {i+1}/{len(text_parts)}...")
                
                # Pausa entre partes para evitar rate limiting
                if i > 0:
                    print("Aguardando 3 segundos para evitar rate limiting...")
                    time.sleep(3)
                
                # Tentar gerar áudio com retry
                success = False
                max_retries = 3
                
                for attempt in range(max_retries):
                    try:
                        # Gerar áudio com gTTS
                        tts = gTTS(text=part, lang=self.language, slow=False)
                        
                        # Salvar temporariamente
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                        temp_file.close()  # Fechar o arquivo antes de salvar
                        tts.save(temp_file.name)
                        
                        # Carregar e processar áudio
                        audio = AudioSegment.from_mp3(temp_file.name)
                        
                        # Aplicar velocidade se necessário
                        if self.speed != 1.0:
                            audio = speedup(audio, playback_speed=self.speed)
                        
                        audio_segments.append(audio)
                        success = True
                        
                        # Limpar arquivo temporário
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass  # Ignorar erros de limpeza
                        
                        break  # Sucesso, sair do loop de retry
                        
                    except Exception as e:
                        print(f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}")
                        if attempt < max_retries - 1:
                            # Aumentar tempo de espera progressivamente para rate limiting
                            wait_time = 5 + (attempt * 3)  # 5s, 8s, 11s
                            print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                            time.sleep(wait_time)
                        else:
                            print(f"ERRO: Falha ao gerar áudio após {max_retries} tentativas")
                            print("Tentando usar TTS local como fallback...")
                            # Tentar TTS local como fallback
                            local_result = self.text_to_speech_local(part, f"temp_part_{i+1}")
                            if local_result:
                                audio = AudioSegment.from_mp3(local_result)
                                audio_segments.append(audio)
                                try:
                                    os.unlink(local_result)
                                except:
                                    pass
                                success = True
                            else:
                                return None
                
                if not success:
                    return None
            
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
    
    def text_to_speech_local(self, text: str, output_filename: str) -> str:
        """
        Fallback: Converte texto em fala usando TTS local (pyttsx3)
        """
        try:
            engine = pyttsx3.init()
            
            # Configurar propriedades da voz
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', int(200 * self.speed))  # Velocidade da fala
            engine.setProperty('volume', 0.9)
            
            # Salvar em arquivo
            output_path = os.path.join(self.output_dir, f"{output_filename}.wav")
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            # Converter WAV para MP3
            audio = AudioSegment.from_wav(output_path)
            mp3_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
            audio.export(mp3_path, format="mp3")
            
            # Limpar arquivo WAV
            try:
                os.unlink(output_path)
            except:
                pass
            
            print(f"Áudio local salvo em: {mp3_path}")
            return mp3_path
            
        except Exception as e:
            print(f"Erro no TTS local: {str(e)}")
            return None

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
