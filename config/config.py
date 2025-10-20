"""
Configurações do gerador de vídeos bíblicos
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# YouTube API
YOUTUBE_CLIENT_SECRET_FILE = 'client_secret.json'
YOUTUBE_TOKEN_FILE = 'token.json'

# Pexels API
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

# Configurações de vídeo
OUTPUT_DIR = 'output'
VIDEO_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'videos')
AUDIO_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'audio')
TEMP_DIR = os.path.join(OUTPUT_DIR, 'temp')
PEXELS_VIDEOS_DIR = os.path.join(OUTPUT_DIR, 'pexels_videos')
SUBTITLES_DIR = os.path.join(OUTPUT_DIR, 'subtitles')

# Configurações de áudio
AUDIO_LANGUAGE = os.getenv('AUDIO_LANGUAGE', 'en')
AUDIO_SPEED = float(os.getenv('AUDIO_SPEED', '1.0'))

# Configurações de vídeo do Pexels
PEXELS_VIDEO_DURATION = 30  # segundos por vídeo
PEXELS_VIDEO_QUALITY = 'large'

# Configurações de publicação
DEFAULT_PRIVACY_STATUS = 'private'
DEFAULT_CATEGORY_ID = '22'  # People & Blogs

# ==========================================
# SISTEMA DE CONFIGURAÇÃO PERSONALIZADA
# ==========================================

class VideoConfig:
    """Classe para gerenciar configurações personalizadas do vídeo"""
    
    def __init__(self):
        self.config_file = 'video_config.json'
        self.default_config = {
            'subject': 'livro-biblico',
            'duration': 'auto',  # 'auto' ou número em minutos
            'voice_speed': 1.0,  # Velocidade da voz (0.5 a 3.0, 1.0 = normal)
            'voice_gender': 'female',  # 'male' ou 'female'
            'voice_volume': 1.0,  # Volume da voz (0.0 a 2.0)
            'video_quality': 'high',  # 'low', 'medium', 'high'
            'video_download_multiplier': 2,  # Multiplicador para downloads de vídeos (2 = dobro, 3 = triplo, etc)
            'background_music': True,
            'background_music_volume': 0.3,
            'video_style': 'calm',  # 'dynamic', 'calm', 'dramatic'
            'custom_queries': [],  # queries personalizadas para busca de vídeos
            'youtube_settings': {
                'privacy': 'private',
                'category': '22',
                'auto_publish': False
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Carrega configurações do arquivo ou usa padrões"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Mesclar com padrões para garantir que todas as chaves existam
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    return config
        except Exception as e:
            print(f"Aviso: Erro ao carregar configurações: {str(e)}")
        
        return self.default_config.copy()
    
    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {str(e)}")
    
    def get(self, key, default=None):
        """Obtém valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Define valor de configuração"""
        self.config[key] = value
    
    def update(self, updates):
        """Atualiza múltiplas configurações"""
        self.config.update(updates)
        self.save_config()
    
    def reset_to_default(self):
        """Reset para configurações padrão"""
        self.config = self.default_config.copy()
        self.save_config()
    
    def get_subject_options(self):
        """Retorna opções disponíveis para assunto"""
        return {
            'livro-biblico': 'Livro Bíblico Completo',
            'capitulo-biblico': 'Capítulo Bíblico Específico',
            'versiculo-especifico': 'Versículo Específico',
            'estudo-biblico': 'Estudo Bíblico',
            'devocional': 'Devocional Diário',
            'historia-biblica': 'História Bíblica',
            'salmos': 'Salmos e Louvores',
            'proverbios': 'Provérbios de Sabedoria'
        }
    
    def get_voice_options(self):
        """Retorna opções de voz disponíveis"""
        return {
            'female': 'Voz Feminina',
            'male': 'Voz Masculina'
        }
    
    def get_quality_options(self):
        """Retorna opções de qualidade de vídeo"""
        return {
            'low': 'Baixa (720p)',
            'medium': 'Média (1080p)',
            'high': 'Alta (4K)'
        }
    
    def get_style_options(self):
        """Retorna opções de estilo"""
        return {
            'video_style': {
                'dynamic': 'Dinâmico (música e transições rápidas)',
                'calm': 'Calmo (música suave e transições lentas)',
                'dramatic': 'Dramático (efeitos sonoros e visuais marcantes)'
            }
        }
    
    def validate_config(self):
        """Valida configurações atuais"""
        errors = []
        
        # Validar velocidade da voz
        if not isinstance(self.config['voice_speed'], (int, float)) or self.config['voice_speed'] < 0.5 or self.config['voice_speed'] > 3.0:
            errors.append("Velocidade da voz deve estar entre 0.5 e 3.0")
        
        # Validar duração
        if self.config['duration'] != 'auto':
            try:
                duration = float(self.config['duration'])
                if duration < 1 or duration > 180:
                    errors.append("Duração deve estar entre 1 e 180 minutos")
            except ValueError:
                errors.append("Duração deve ser 'auto' ou um número válido")
        
        # Validar volume da música de fundo
        if not isinstance(self.config['background_music_volume'], (int, float)) or self.config['background_music_volume'] < 0 or self.config['background_music_volume'] > 1:
            errors.append("Volume da música de fundo deve estar entre 0 e 1")
        
        # Validar volume da voz
        if not isinstance(self.config['voice_volume'], (int, float)) or self.config['voice_volume'] < 0 or self.config['voice_volume'] > 2:
            errors.append("Volume da voz deve estar entre 0 e 2")
        
        # Validar multiplicador de download de vídeos
        if 'video_download_multiplier' in self.config:
            if not isinstance(self.config['video_download_multiplier'], (int, float)) or self.config['video_download_multiplier'] < 1 or self.config['video_download_multiplier'] > 10:
                errors.append("Multiplicador de download de vídeos deve estar entre 1 e 10")
        
        return errors
    
    def get_bible_text_generator(self):
        """
        Retorna uma instância configurada do BibleTextGenerator (English only)
        
        Returns:
            BibleTextGenerator configurado para inglês
        """
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from text.bible_text_generator import BibleTextGenerator
            
            return BibleTextGenerator()
        except Exception as e:
            print(f"[ERROR] Error creating BibleTextGenerator: {str(e)}")
            return None
    
    def get_bible_data_creator(self):
        """
        Retorna uma instância do BibleDataCreator
        
        Returns:
            BibleDataCreator para manipular dados bíblicos
        """
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from bible_data.bible_data_creator import BibleDataCreator
            
            return BibleDataCreator()
        except Exception as e:
            print(f"[ERROR] Erro ao criar BibleDataCreator: {str(e)}")
            return None

# Instância global de configuração
video_config = VideoConfig()
