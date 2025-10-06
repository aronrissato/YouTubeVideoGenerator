import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.resize import resize
from moviepy.editor import CompositeAudioClip


# Constantes
PASTA_VIDEOS = "videos"
PASTA_MUSICA = "music"
ARQUIVO_SAIDA = "video_final.mp4"
TAMANHO_FINAL = (1920, 1080)  # Full HD


def unify_video_audio(duracao_final):
    videos = sorted(
        [
            os.path.join(PASTA_VIDEOS, f)
            for f in os.listdir(PASTA_VIDEOS)
            if f.endswith(".mp4")
        ]
    )

    clips = []
    duracao_acumulada = 0
    index = 0

    while duracao_acumulada < duracao_final:
        video_path = videos[index % len(videos)]  # loop infinito sobre a lista
        clip = VideoFileClip(video_path)
        tempo_restante = duracao_final - duracao_acumulada
        duracao_uso = min(clip.duration, tempo_restante)

        # Recorta a parte necessária e estica para ocupar a tela inteira
        clip_sub = resize(clip.subclip(0, duracao_uso), newsize=TAMANHO_FINAL)

        clips.append(clip_sub)
        duracao_acumulada += duracao_uso
        index += 1

    video_final = concatenate_videoclips(clips, method="compose")

    # Música de fundo (opcional)
    musicas = [f for f in os.listdir(PASTA_MUSICA) if f.endswith(".mp3")]
    if musicas:
        trilha = AudioFileClip(os.path.join(PASTA_MUSICA, musicas[0])).subclip(
            0, video_final.duration
        )
        video_final = video_final.set_audio(trilha)

    video_final.write_videofile(
        ARQUIVO_SAIDA,
        fps=24,
        codec="libx264",
        threads=8,
        audio_codec="aac",
        preset="ultrafast",
        bitrate="2000k",
        logger="bar",
    )


def unify_with_speech():
    from moviepy.audio.fx.all import volumex
    from moviepy.editor import CompositeAudioClip, concatenate_videoclips

    # Caminhos
    pasta_musica = PASTA_MUSICA
    caminho_fala = os.path.join(PASTA_MUSICA, "voice.mp3")

    # Carregar o áudio da fala (speech)
    fala_audio = AudioFileClip(caminho_fala)
    duracao_fala = fala_audio.duration

    # Carregar a música de fundo (assuma que há apenas 1 mp3 além do voice)
    arquivos_mp3 = [
        f for f in os.listdir(pasta_musica) if f.endswith(".mp3") and f != "voice.mp3"
    ]
    if not arquivos_mp3:
        raise FileNotFoundError("Nenhuma música de fundo encontrada na pasta 'music'.")

    caminho_musica = os.path.join(pasta_musica, arquivos_mp3[0])
    musica_fundo = (
        AudioFileClip(caminho_musica).subclip(0, duracao_fala).fx(volumex, 0.1)
    )

    # Misturar fala com música
    audio_mixado = CompositeAudioClip([musica_fundo, fala_audio])

    # Carregar os vídeos da pasta
    pasta_videos = PASTA_VIDEOS
    arquivos_video = [f for f in os.listdir(pasta_videos) if f.endswith(".mp4")]
    clips = []
    duracao_acumulada = 0
    index = 0

    # Repete os vídeos até preencher toda a fala
    while duracao_acumulada < duracao_fala:
        video_path = os.path.join(
            pasta_videos, arquivos_video[index % len(arquivos_video)]
        )
        clip = VideoFileClip(video_path)
        tempo_restante = duracao_fala - duracao_acumulada
        duracao_uso = min(clip.duration, tempo_restante)

        # Redimensiona e recorta o trecho necessário
        clip_sub = resize(clip.subclip(0, duracao_uso), newsize=TAMANHO_FINAL)
        clips.append(clip_sub)

        duracao_acumulada += duracao_uso
        index += 1

    video_final = concatenate_videoclips(clips, method="compose")

    video_final = video_final.set_audio(audio_mixado)

    # Salvar o vídeo final
    video_final.write_videofile(
        "video_final.mp4", codec="libx264", audio_codec="aac", logger="bar"
    )


if __name__ == "__main__":
    unify_video_audio(duracao_final)
