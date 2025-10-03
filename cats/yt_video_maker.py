import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.file_credencials import get_credentials
from common.file_unify import unify_video_audio
from common.file_music import get_music
from common.file_video import get_video
from common.file_manager import delete_files
from common.file_publish import publish_video
from common.file_description import get_description
from datetime import datetime
from dotenv import load_dotenv


def main():
    load_dotenv()

    # get_video configs
    KEY_PEXELS = os.getenv("KEY_PEXELS")
    DOWNLOAD_FOLDER = "videos"
    VIDEOS_COUNT = 3  # how many videos from Pexes API
    ORIENTATION = "landscape"

    SEARCH_QUERY = "cats"

    # get_description configs
    KEY_GEMINI = os.getenv("KEY_GEMINI")
    SELECT_MODEL = "gemini-1.5-flash"
    PROMPT_GEMINI = f"""Gere um título e uma descrição inspirado no dia da semana de hoje, em ingles para um vídeo do YouTube. 
    Estou te usando como prompt então envie exatamente no formato que eu te pedir, somente uma opção.

    O conteúdo do vídeo é: {SEARCH_QUERY}

    Formato OBRIGATÓRIO de retorno! (Sem asterisco antes ou depois de Título e Descrição):
    Título: <Título aqui>
    Descrição: <Descrição aqui>"""

    # get_music config
    AUDIO = "https://www.youtube.com/watch?v=fg_wh-qqDf0"  # audio from youtube

    # unify config
    DURACAO_FINAL = 120  # 10 minutes

    # publish_video configs
    TAGS = [
        "gato",
        "vídeo para gatos",
        "música relaxante",
        "cat video",
        "cat tv",
        "relaxing music for cats",
        "cats",
        "music for cats",
        "musica para gatos",
        "cute cats",
    ]
    CATEGORY_ID = "15"  #  Pets & Animals
    CLIENT_SECRET_FILE = "client_secret.json"
    TOKEN_FILE = "token.json"
    VIDEO_FILE = "video_final.mp4"

    ## ----------------------------------------------

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Getting videos:")
    get_video(KEY_PEXELS, DOWNLOAD_FOLDER, SEARCH_QUERY, VIDEOS_COUNT, ORIENTATION)

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Getting title and describing:")
    returned_title_desc = get_description(KEY_GEMINI, SELECT_MODEL, PROMPT_GEMINI)

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Getting music from YouTube:")
    get_music(AUDIO)

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Unify music and video:")
    unify_video_audio(DURACAO_FINAL)

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Getting tokens")
    creds = get_credentials(CLIENT_SECRET_FILE, TOKEN_FILE)

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Publishing...")
    publish_video(
        returned_title_desc,
        TAGS,
        CATEGORY_ID,
        creds,
        VIDEO_FILE,
    )

    agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    print(f"{agora} - Deleting generated files.")
    delete_files(os.path.dirname(__file__))
    input("Done!")


if __name__ == "__main__":
    main()
