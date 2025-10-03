"""
Configurações do gerador de vídeos bíblicos
"""
import os
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
VIDEO_OUTPUT_DIR = 'output'
AUDIO_OUTPUT_DIR = 'audio'
TEMP_DIR = 'temp'

# Configurações de áudio
AUDIO_LANGUAGE = 'pt'
AUDIO_SPEED = 1.0

# Configurações de vídeo do Pexels
PEXELS_VIDEO_DURATION = 30  # segundos por vídeo
PEXELS_VIDEO_QUALITY = 'large'

# Configurações de publicação
DEFAULT_PRIVACY_STATUS = 'private'
DEFAULT_CATEGORY_ID = '22'  # People & Blogs
