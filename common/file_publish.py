import os
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

video_file = os.path.abspath("video_final.mp4")
subtitles_file = os.path.abspath("music/voice.srt")


def publish_video(returned_title_desc, tags, category_id, creds, video_file):
    youtube = build("youtube", "v3", credentials=creds)

    titulo, descricao = extract_title_and_description(returned_title_desc)

    request_body = {
        "snippet": {
            "title": titulo,
            "description": descricao,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {"privacyStatus": "public", "madeForKids": False},
    }

    media_file = MediaFileUpload(
        video_file, chunksize=-1, resumable=True, mimetype="video/*"
    )

    print("Iniciando envio para o YouTube...")
    request = youtube.videos().insert(
        part="snippet,status", body=request_body, media_body=media_file
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload em andamento: {int(status.progress() * 100)}%")

    print(
        f"{datetime.datetime.now().strftime('%d-%m-%Y')} - Vídeo enviado! Link: https://www.youtube.com/watch?v={response['id']}"
    )

    return response["id"]


def upload_subtitle(youtube, video_id, srt_path, language="en"):
    media_file = MediaFileUpload(srt_path, mimetype="application/octet-stream")

    subtitle_body = {
        "snippet": {
            "videoId": video_id,
            "language": language,
            "name": "English",
            "isDraft": False,
        }
    }

    print("Sending subtitles...")
    request = youtube.captions().insert(
        part="snippet", body=subtitle_body, media_body=media_file
    )
    response = request.execute()
    print("Subtitle sent sucessfully.")


def extract_title_and_description(text):
    lines = text.strip().splitlines()
    titulo = ""
    descricao = ""
    for line in lines:
        if line.lower().startswith("título:") or line.lower().startswith("title:"):
            titulo = line.split(":", 1)[1].strip()
        elif line.lower().startswith("descrição:") or line.lower().startswith(
            "description:"
        ):
            descricao = line.split(":", 1)[1].strip()
    return titulo, descricao


if __name__ == "__main__":
    from file_credencials import get_credentials

    CLIENT_SECRET_FILE = """C:\\Users\\rafae\\OneDrive\\Área de Trabalho\\YouTubeVideoGenerator\\bible\\client_secret.json"""
    TOKEN_FILE = "token.json"
    creds = get_credentials(CLIENT_SECRET_FILE, TOKEN_FILE)
    upload_subtitle(
        build("youtube", "v3", credentials=creds),
        # "Tk_FoY0KX0E",
        """C:\\Users\\rafae\\OneDrive\\Área de Trabalho\\YouTubeVideoGenerator\\bible\\music\\voice.srt""",
        "en",
    )
