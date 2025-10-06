import sys
import os
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.file_credencials import get_credentials
from common.file_unify import unify_with_speech
from common.file_music import get_music
from common.file_video import get_video
from common.file_manager import delete_files
from common.file_publish import publish_video, upload_subtitle
from common.file_description import get_description
from common.file_speech import get_speech_mp3
from prompt_chapters import get_speech
from file_chapters import get_chapter
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
import subprocess


def cleanup_files():
    """Remove arquivos temporários em caso de erro"""
    folders_to_clean = ["videos", "music"]
    files_to_clean = ["video_final.mp4", "token.json"]
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned folder: {folder}")
    
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned file: {file}")


def main():
    try:
        # Load environment variables
        load_dotenv()
        
        chapters = "chapters.txt"

        # get_video configs
        KEY_PEXELS = os.getenv("KEY_PEXELS")
        if not KEY_PEXELS:
            print("ERROR: KEY_PEXELS not found in .env file")
            return
        DOWNLOAD_FOLDER = "videos"
        VIDEOS_COUNT = "6"  # how many videos from Pexes API
        ORIENTATION = "landscape"
        IDIOMA = "inglês"
        SEARCH_QUERY = "christian"

        # get_description configs
        KEY_GEMINI = os.getenv("KEY_GEMINI")
        if not KEY_GEMINI:
            print("ERROR: KEY_GEMINI not found in .env file")
            return
        SELECT_MODEL = "gemini-1.5-flash"
        PROMPT_DESCRIPTION = f"""Gere um título e uma descrição {IDIOMA} para um vídeo no YouTube.
        Estou te usando como prompt então envie exatamente no formato que eu te pedir, somente uma opção.

        Formato OBRIGATÓRIO de retorno, sem asterisco antes ou depois de Título e Descrição:
        Título: <Título aqui>
        Descrição: <Descrição aqui>

        O conteúdo do vídeo é sobre o capítulo da bíblia:"""

        # get_music config
        URL_AUDIO = "https://www.youtube.com/watch?v=fg_wh-qqDf0"  # audio from youtube

        # publish_video configs
        TAGS = [
            "angel messages",
            "daily angel message",
            "spiritual guidance",
            "divine message",
            "faith",
            "God",
            "Jesus",
            "guardian angel",
            "bible verses",
            "christian inspiration",
            "lightworker",
            "peace",
            "hope",
            "love",
            "spiritual awakening",
            "prayer",
            "healing",
            "angelic signs",
            "archangel michael",
            "message from heaven",
        ]
        CATEGORY_ID = "22"  #  People & Blogs
        CLIENT_SECRET_FILE = "client_secret_475779770650-h2j3cnj80nfinfcsfr4qi5s89lqvkogo.apps.googleusercontent.com.json"
        TOKEN_FILE = "token.json"
        VIDEO_FILE = "video_final.mp4"

        ## ----------------------------------------------

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Getting videos")
        get_video(KEY_PEXELS, DOWNLOAD_FOLDER, SEARCH_QUERY, VIDEOS_COUNT, ORIENTATION)

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Getting text and chapter for the speech using Gemini")
        return_speech = get_speech(KEY_GEMINI, SELECT_MODEL)

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Getting title and description about the chapter using Gemini")
        returned_title_desc = get_description(
            KEY_GEMINI, SELECT_MODEL, PROMPT_DESCRIPTION + return_speech["chapter"]
        )

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Getting music from YouTube")
        get_music(URL_AUDIO)

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Getting speech to mp3")
        get_speech_mp3(return_speech["text"])

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Generating subtitles")
        generate_subtitles_external()

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Unify music and video")
        unify_with_speech()

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Getting tokens")
        creds = get_credentials(CLIENT_SECRET_FILE, TOKEN_FILE)

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Publishing...")
        video_id = publish_video(
            returned_title_desc,
            TAGS,
            CATEGORY_ID,
            creds,
            VIDEO_FILE,
        )

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Uploading subtitles.")
        youtube = build("youtube", "v3", credentials=creds)
        upload_subtitle(youtube, video_id, "music/voice.srt")

        agora = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
        print(f"{agora} - Deleting generated files.")
        delete_files(
            "C:\\Users\\rafae\\OneDrive\\Área de Trabalho\\YouTubeVideoGenerator\\bible"
        )
        input("Done!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Cleaning up temporary files...")
        cleanup_files()
        print("Cleanup completed.")
        input("Press Enter to exit...")


def generate_subtitles_external():
    python311 = r"C:\Users\rafae\AppData\Local\Programs\Python\Python311\python.exe"
    script_path = r"C:\Users\rafae\OneDrive\Área de Trabalho\YouTubeVideoGenerator\bible\generate_subtitles.py"
    subprocess.run([python311, script_path], check=True)


if __name__ == "__main__":
    main()
