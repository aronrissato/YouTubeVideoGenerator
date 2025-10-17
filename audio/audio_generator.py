"""
Gerador de áudio/narração do texto bíblico
"""
import os
import math
import time
import asyncio
import warnings
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import tempfile
import pyttsx3
from config.config import video_config, AUDIO_OUTPUT_DIR

# Import Edge TTS (Microsoft - melhor qualidade, gratuito, sempre funciona)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("Edge TTS não disponível. Instale com: pip install edge-tts")

# Import Azure Speech Services (opcional)
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Azure Speech Services não disponível. Instale com: pip install azure-cognitiveservices-speech")

class AudioGenerator:
    def __init__(self, language='en', speed=1.0):
        # Usar configurações personalizadas se disponíveis
        self.language = video_config.get('language', language)
        self.speed = video_config.get('voice_speed', speed)
        self.voice_gender = video_config.get('voice_gender', 'female')
        self.voice_volume = video_config.get('voice_volume', 1.0)
        self.output_dir = AUDIO_OUTPUT_DIR
        self._azure_warning_shown = False  # Flag para evitar mensagens repetidas do Azure
        
        # Criar diretório de saída se não existir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def text_to_speech(self, text: str, output_filename: str) -> str:
        """
        Converte texto em fala e retorna o caminho do arquivo de áudio
        Ordem de prioridade:
        1. Edge TTS (Microsoft) - Melhor qualidade, gratuito, sempre funciona
        2. Azure TTS - Requer API key, alta qualidade
        3. TTS Local (pyttsx3) - Offline, qualidade média
        4. gTTS - Online, qualidade básica
        """
        try:
            # Validar texto de entrada
            if not text or not text.strip():
                print("ERRO: Texto vazio fornecido para geração de áudio")
                return None
            
            # Dividir texto em partes menores se muito longo
            max_length = 5000
            text_parts = self._split_text(text, max_length)
            
            # Verificar se temos partes válidas
            if not text_parts:
                print("ERRO: Nenhuma parte válida de texto encontrada")
                return None
            
            print(f"Texto dividido em {len(text_parts)} partes")
            audio_segments = []
            
            for i, part in enumerate(text_parts):
                print(f"Gerando áudio parte {i+1}/{len(text_parts)}...")
                
                # Verificar se a parte não está vazia
                if not part or not part.strip():
                    print(f"Aviso: Parte {i+1} está vazia, pulando...")
                    continue
                
                # PRIMEIRA OPÇÃO: Edge TTS (Microsoft - MELHOR OPÇÃO!)
                print("Tentando Edge TTS (Microsoft) - primeira opção...")
                edge_result = self.text_to_speech_edge(part, f"temp_part_{i+1}")
                
                if edge_result:
                    try:
                        audio = AudioSegment.from_mp3(edge_result)
                        
                        # Aplicar volume da voz se necessário
                        if self.voice_volume != 1.0:
                            audio = audio + (20 * math.log10(self.voice_volume))
                        
                        audio_segments.append(audio)
                        # Limpar arquivo temporário
                        try:
                            os.unlink(edge_result)
                        except:
                            pass
                        print("Edge TTS funcionou perfeitamente!")
                        continue  # Sucesso, ir para próxima parte
                    except Exception as e:
                        print(f"Erro ao processar áudio Edge TTS: {str(e)}")
                        try:
                            os.unlink(edge_result)
                        except:
                            pass
                
                # SEGUNDA OPÇÃO: Azure TTS (fallback)
                if not self._azure_warning_shown:
                    print("Edge TTS falhou, tentando Azure TTS...")
                azure_result = None
                max_azure_retries = 2
                
                for azure_attempt in range(max_azure_retries):
                    azure_result = self.text_to_speech_azure(part, f"temp_part_{i+1}")
                    if azure_result:
                        break
                    elif azure_attempt < max_azure_retries - 1:
                        time.sleep(2)
                
                if azure_result:
                    try:
                        audio = AudioSegment.from_mp3(azure_result)
                        
                        # Aplicar volume da voz se necessário
                        if self.voice_volume != 1.0:
                            audio = audio + (20 * math.log10(self.voice_volume))
                        
                        audio_segments.append(audio)
                        try:
                            os.unlink(azure_result)
                        except:
                            pass
                        print("Azure TTS funcionou perfeitamente!")
                        continue
                    except Exception as e:
                        print(f"Erro ao processar áudio Azure: {str(e)}")
                        try:
                            os.unlink(azure_result)
                        except:
                            pass
                
                # TERCEIRA OPÇÃO: TTS Local (fallback)
                print("Azure TTS falhou, tentando TTS local...")
                local_result = self.text_to_speech_local(part, f"temp_part_{i+1}")
                
                if local_result:
                    try:
                        audio = AudioSegment.from_mp3(local_result)
                        
                        # Aplicar volume da voz se necessário
                        if self.voice_volume != 1.0:
                            audio = audio + (20 * math.log10(self.voice_volume))
                        
                        audio_segments.append(audio)
                        try:
                            os.unlink(local_result)
                        except:
                            pass
                        print("TTS local funcionou perfeitamente!")
                        continue
                    except Exception as e:
                        print(f"Erro ao processar áudio local: {str(e)}")
                        try:
                            os.unlink(local_result)
                        except:
                            pass
                
                # QUARTA OPÇÃO: gTTS (último fallback)
                print("TTS local falhou, tentando gTTS como último fallback...")
                
                if i > 0:
                    time.sleep(3)
                
                success = False
                max_retries = 3
                
                for attempt in range(max_retries):
                    try:
                        if not part or not part.strip():
                            print(f"Erro: Texto vazio na tentativa {attempt + 1} do gTTS")
                            break
                        
                        tts = gTTS(text=part, lang=self.language, slow=False)
                        
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                        temp_file.close()
                        tts.save(temp_file.name)
                        
                        audio = AudioSegment.from_mp3(temp_file.name)
                        
                        # gTTS usa velocidade fixa 1.0x (velocidade normal para melhor naturalidade)
                        gtts_speed = 1.0
                        print(f"gTTS usando velocidade fixa: {gtts_speed}x (Edge TTS configurado: {self.speed}x)")
                        # Não precisa aplicar velocidade pois já está em 1.0x (normal)
                        
                        # Aplicar volume da voz se necessário
                        if self.voice_volume != 1.0:
                            audio = audio + (20 * math.log10(self.voice_volume))
                        
                        audio_segments.append(audio)
                        success = True
                        
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                        
                        print("gTTS funcionou como fallback!")
                        break
                        
                    except Exception as e:
                        error_msg = str(e) if str(e).strip() else "Erro desconhecido no gTTS"
                        print(f"gTTS tentativa {attempt + 1}/{max_retries} falhou: {error_msg}")
                        
                        if "No text to speak" in error_msg or "text" in error_msg.lower():
                            print("Erro relacionado ao texto, não tentando novamente")
                            break
                        
                        if attempt < max_retries - 1:
                            wait_time = 5 + (attempt * 3)
                            print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                            time.sleep(wait_time)
                        else:
                            print(f"ERRO: Todas as opções de TTS falharam para esta parte")
                            return None
                
                if not success:
                    return None
            
            # Verificar se temos segmentos de áudio
            if not audio_segments:
                print("ERRO: Nenhum segmento de áudio foi gerado")
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
        
        # Filtrar partes vazias
        parts = [part for part in parts if part and part.strip()]
        
        return parts
    
    def text_to_speech_edge(self, text: str, output_filename: str) -> str:
        """
        Melhor opção: Converte texto em fala usando Edge TTS (Microsoft)
        - Vozes neurais de altíssima qualidade
        - Gratuito e sem necessidade de API key
        - Sempre funciona (com retry)
        - Suporta controle de velocidade nativo
        """
        if not EDGE_TTS_AVAILABLE:
            return None
        
        # Tentar múltiplas vezes (Edge TTS pode falhar com 403 ocasionalmente)
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Validar texto antes de processar
                if not text or not text.strip():
                    print("Erro: Texto vazio fornecido para Edge TTS")
                    return None
                
                # Obter voz baseada no idioma e gênero
                voice_name = self._get_edge_voice_name()
                
                # Converter velocidade para formato Edge TTS
                # self.speed é um float (ex: 1.0, 1.2, 0.8)
                # Edge TTS usa formato de porcentagem (ex: "+20%", "-30%")
                speed_percentage = int((self.speed - 1.0) * 100)
                if speed_percentage >= 0:
                    rate = f"+{speed_percentage}%"
                else:
                    rate = f"{speed_percentage}%"
                
                if attempt == 0:
                    print(f"Edge TTS usando voz: {voice_name}")
                    print(f"Edge TTS aplicando velocidade configurada: {self.speed}x ({rate})")
                else:
                    print(f"Edge TTS tentativa {attempt + 1}/{max_retries}...")
                
                # Criar arquivo de saída
                output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
                
                # Função assíncrona para gerar áudio
                async def generate_audio():
                    communicate = edge_tts.Communicate(text, voice=voice_name, rate=rate)
                    await communicate.save(output_path)
                
                # Executar função assíncrona
                asyncio.run(generate_audio())
                
                # Verificar se arquivo foi criado
                if not os.path.exists(output_path):
                    print("Erro: Arquivo de áudio não foi criado pelo Edge TTS")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                
                print(f"Edge TTS funcionou: {output_path}")
                return output_path
                
            except Exception as e:
                error_msg = str(e) if str(e).strip() else "Erro desconhecido no Edge TTS"
                
                # Extrair apenas código de erro e tipo (sem URL completa por segurança)
                error_code = "desconhecido"
                error_type = "erro"
                if "401" in error_msg:
                    error_code = "401"
                elif "403" in error_msg:
                    error_code = "403"
                if "Invalid response status" in error_msg:
                    error_type = "Invalid response status"
                elif "ConnectionError" in error_msg:
                    error_type = "ConnectionError"
                
                # Se for erro 403/401 ou erro de conexão, tentar novamente
                if "403" in error_msg or "401" in error_msg or "Invalid response status" in error_msg or "ConnectionError" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = 2 + (attempt * 2)  # 2s, 4s, 6s
                        print(f"Edge TTS erro temporário (tentativa {attempt + 1}/{max_retries}): {error_code} - {error_type}")
                        print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                        time.sleep(wait_time)
                        continue
                
                print(f"Erro no Edge TTS: {error_code} - {error_type}")
                return None
        
        print("Edge TTS falhou após múltiplas tentativas")
        return None
    
    def _get_edge_voice_name(self) -> str:
        """Retorna o nome da voz Edge TTS baseada no idioma e gênero configurados"""
        
        # Mapeamento de vozes neurais Edge TTS por idioma e gênero
        edge_voices = {
            'pt': {
                'female': 'pt-BR-FranciscaNeural',
                'male': 'pt-BR-AntonioNeural'
            },
            'pt-BR': {
                'female': 'pt-BR-FranciscaNeural',
                'male': 'pt-BR-AntonioNeural'
            },
            'en': {
                'female': 'en-US-AriaNeural',
                'male': 'en-US-BrianMultilingualNeural'
            },
            'en-US': {
                'female': 'en-US-AriaNeural',
                'male': 'en-US-BrianMultilingualNeural'
            },
            'en-GB': {
                'female': 'en-GB-SoniaNeural',
                'male': 'en-GB-RyanNeural'
            },
            'es': {
                'female': 'es-ES-ElviraNeural',
                'male': 'es-ES-AlvaroNeural'
            },
            'fr': {
                'female': 'fr-FR-DeniseNeural',
                'male': 'fr-FR-HenriNeural'
            },
            'de': {
                'female': 'de-DE-KatjaNeural',
                'male': 'de-DE-ConradNeural'
            },
            'it': {
                'female': 'it-IT-ElsaNeural',
                'male': 'it-IT-DiegoNeural'
            }
        }
        
        language = self.language
        gender = self.voice_gender
        
        # Buscar voz específica
        if language in edge_voices and gender in edge_voices[language]:
            return edge_voices[language][gender]
        
        # Fallback para inglês se idioma não encontrado
        if 'en' in edge_voices and gender in edge_voices['en']:
            print(f"Voz Edge TTS não encontrada para {language}, usando inglês como fallback")
            return edge_voices['en'][gender]
        
        # Fallback padrão
        print("Usando voz Edge TTS padrão: en-US-AriaNeural")
        return 'en-US-AriaNeural'
    
    def text_to_speech_azure(self, text: str, output_filename: str) -> str:
        """
        Opção premium: Converte texto em fala usando Azure Speech Services com vozes neurais
        """
        if not AZURE_AVAILABLE:
            return None
            
        try:
            # Configurar Azure Speech Services
            speech_key = os.getenv('AZURE_SPEECH_KEY')
            speech_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
            
            if not speech_key:
                if not self._azure_warning_shown:
                    print("Azure Speech Key não configurada, pulando Azure TTS")
                    self._azure_warning_shown = True
                return None
            
            # Configurar voz neural baseada no idioma e gênero
            voice_name = self._get_azure_voice_name()
            
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Configurar velocidade da fala
            speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
            
            # Criar arquivo de saída temporário
            temp_output = os.path.join(self.output_dir, f"{output_filename}_temp.mp3")
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_output)
            
            # Criar synthesizer
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            
            # Sintetizar fala
            print(f"Azure TTS usando voz neural: {voice_name}")
            print(f"Azure TTS usando velocidade fixa: 1.0x (Edge TTS configurado: {self.speed}x)")
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Azure TTS sempre usa velocidade 1.0x (sem modificações de speed)
                # Apenas renomear o arquivo temporário
                output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
                os.rename(temp_output, output_path)
                
                print(f"Azure TTS funcionou: {output_path}")
                return output_path
            else:
                print(f"Azure TTS falhou: {result.reason}")
                # Limpar arquivo temporário se houver
                try:
                    if os.path.exists(temp_output):
                        os.unlink(temp_output)
                except:
                    pass
                return None
                
        except Exception as e:
            print(f"Erro no Azure TTS: {str(e)}")
            return None
    
    def _get_azure_voice_name(self) -> str:
        """Retorna o nome da voz neural Azure baseada no idioma e gênero configurados"""
        
        # Mapeamento de vozes neurais Azure por idioma e gênero
        neural_voices = {
            'pt': {
                'female': 'pt-BR-FranciscaNeural',
                'male': 'pt-BR-AntonioNeural'
            },
            'pt-BR': {
                'female': 'pt-BR-FranciscaNeural', 
                'male': 'pt-BR-AntonioNeural'
            },
            'en': {
                'female': 'en-US-AriaNeural',
                'male': 'en-US-BrianMultilingualNeural'
            },
            'en-US': {
                'female': 'en-US-AriaNeural',
                'male': 'en-US-BrianMultilingualNeural'
            },
            'en-GB': {
                'female': 'en-GB-SoniaNeural',
                'male': 'en-GB-RyanNeural'
            },
            'es': {
                'female': 'es-ES-ElviraNeural',
                'male': 'es-ES-AlvaroNeural'
            },
            'fr': {
                'female': 'fr-FR-DeniseNeural',
                'male': 'fr-FR-HenriNeural'
            },
            'de': {
                'female': 'de-DE-KatjaNeural',
                'male': 'de-DE-ConradNeural'
            },
            'it': {
                'female': 'it-IT-ElsaNeural',
                'male': 'it-IT-DiegoNeural'
            }
        }
        
        language = self.language
        gender = self.voice_gender
        
        # Buscar voz específica
        if language in neural_voices and gender in neural_voices[language]:
            return neural_voices[language][gender]
        
        # Fallback para inglês se idioma não encontrado
        if 'en' in neural_voices and gender in neural_voices['en']:
            print(f"Voz neural não encontrada para {language}, usando inglês como fallback")
            return neural_voices['en'][gender]
        
        # Fallback padrão
        print("Usando voz neural padrão: en-US-AriaNeural")
        return 'en-US-AriaNeural'

    def text_to_speech_local(self, text: str, output_filename: str) -> str:
        """
        Segunda opção: Converte texto em fala usando TTS local melhorado (pyttsx3)
        """
        try:
            # Validar texto antes de processar
            if not text or not text.strip():
                print("Erro: Texto vazio fornecido para TTS local")
                return None
            
            # Limpar texto de caracteres problemáticos
            text = text.strip()
            if len(text) < 3:
                print("Erro: Texto muito curto para TTS local")
                return None
            engine = pyttsx3.init()
            
            # Configurar propriedades da voz com seleção inteligente
            voices = engine.getProperty('voices')
            selected_voice = None
            
            # Lista de vozes a evitar (vozes muito robóticas)
            voices_to_avoid = ['david', 'microsoft david', 'david desktop']
            
            # Mapear idiomas para vozes disponíveis
            lang_voice_map = {
                'pt': ['portuguese', 'brazil', 'pt'],
                'pt-BR': ['portuguese', 'brazil', 'pt'],
                'pt-pt': ['portuguese', 'portugal', 'pt'],
                'en': ['english', 'en-us', 'en-gb'],
                'es': ['spanish', 'es'],
                'fr': ['french', 'fr'],
                'de': ['german', 'de'],
                'it': ['italian', 'it']
            }
            
            # Tentar encontrar voz no idioma desejado
            target_langs = lang_voice_map.get(self.language, ['english'])
            
            # Priorizar vozes femininas ou masculinas conforme configurado
            preferred_gender_keywords = []
            if self.voice_gender == 'female':
                preferred_gender_keywords = ['zira', 'hazel', 'susan', 'female', 'woman']
            else:
                preferred_gender_keywords = ['mark', 'male', 'man']
            
            # Primeira tentativa: encontrar voz no idioma correto e gênero preferido, evitando as robóticas
            for voice in voices:
                voice_name_lower = voice.name.lower()
                voice_id_lower = voice.id.lower()
                
                # Pular vozes muito robóticas
                if any(bad_voice in voice_name_lower for bad_voice in voices_to_avoid):
                    continue
                
                # Verificar se é do idioma correto
                is_correct_language = any(target_lang in voice_name_lower or target_lang in voice_id_lower for target_lang in target_langs)
                
                # Verificar se é do gênero preferido
                is_preferred_gender = any(keyword in voice_name_lower for keyword in preferred_gender_keywords)
                
                if is_correct_language and is_preferred_gender:
                    selected_voice = voice
                    break
            
            # Segunda tentativa: encontrar voz no idioma correto, ignorando gênero
            if not selected_voice:
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    voice_id_lower = voice.id.lower()
                    
                    # Pular vozes muito robóticas
                    if any(bad_voice in voice_name_lower for bad_voice in voices_to_avoid):
                        continue
                    
                    for target_lang in target_langs:
                        if target_lang in voice_name_lower or target_lang in voice_id_lower:
                            selected_voice = voice
                            break
                    
                    if selected_voice:
                        break
            
            # Terceira tentativa: usar qualquer voz que não seja robótica
            if not selected_voice:
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    
                    # Pular vozes muito robóticas
                    if any(bad_voice in voice_name_lower for bad_voice in voices_to_avoid):
                        continue
                    
                    selected_voice = voice
                    break
            
            if selected_voice:
                engine.setProperty('voice', selected_voice.id)
                print(f"TTS local usando voz: {selected_voice.name}")
            else:
                print("Nenhuma voz específica encontrada, usando voz padrão (pode ser robótica)")
            
            # Configurar velocidade e volume otimizados
            # TTS Local sempre usa velocidade 1.0x (sem modificações de speed)
            base_rate = 200
            engine.setProperty('rate', base_rate)
            engine.setProperty('volume', 0.9)
            print(f"TTS local configurado com taxa de fala base: {base_rate}")
            print(f"TTS local usando velocidade fixa: 1.0x (Edge TTS configurado: {self.speed}x)")
            
            # Salvar em arquivo temporário
            output_path = os.path.join(self.output_dir, f"{output_filename}.wav")
            engine.save_to_file(text, output_path)
            
            # Suprimir warnings e erros do espeak/pyttsx3
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                warnings.filterwarnings("ignore", message=".*weakly-referenced object.*")
                try:
                    engine.runAndWait()
                except (ReferenceError, RuntimeError):
                    # Ignorar erros de referência fraca do espeak
                    pass
            
            # Verificar se arquivo foi criado
            if not os.path.exists(output_path):
                print("Erro: Arquivo de áudio não foi criado pelo TTS local")
                return None
            
            # Converter WAV para MP3
            audio = AudioSegment.from_wav(output_path)
            
            # Aplicar volume da voz se necessário
            if self.voice_volume != 1.0:
                audio = audio + (20 * math.log10(self.voice_volume))
            
            mp3_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
            audio.export(mp3_path, format="mp3")
            
            # Limpar arquivo WAV
            try:
                os.unlink(output_path)
            except:
                pass
            
            print(f"TTS local funcionou: {mp3_path}")
            return mp3_path
            
        except Exception as e:
            error_msg = str(e) if str(e).strip() else "Erro desconhecido no TTS local"
            print(f"Erro no TTS local: {error_msg}")
            return None

def main():
    # Exemplo de uso com Edge TTS (melhor qualidade!)
    audio_gen = AudioGenerator(language='pt-BR', speed=1.0)
    
    # Texto de exemplo
    sample_text = """
    No princípio, Deus criou os céus e a terra. E a terra era sem forma e vazia; 
    e havia trevas sobre a face do abismo; e o Espírito de Deus se movia sobre a face das águas.
    E disse Deus: Haja luz. E houve luz.
    """
    
    print("Gerando áudio com Edge TTS (Microsoft) - Melhor qualidade!")
    audio_file = audio_gen.text_to_speech(sample_text, "teste")
    if audio_file:
        duration = audio_gen.get_audio_duration(audio_file)
        print(f"Duração: {duration:.2f} segundos")

if __name__ == "__main__":
    main()
