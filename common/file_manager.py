import os
import shutil


def delete_files(base_dir):
    videos_path = os.path.join(base_dir, "videos")
    musica_path = os.path.join(base_dir, "music")
    video_final_path = os.path.join(base_dir, "video_final.mp4")

    print(f"Tentando apagar: {videos_path}")
    print(f"Tentando apagar: {musica_path}")
    print(f"Tentando apagar: {video_final_path}")

    try:
        shutil.rmtree(videos_path)
        shutil.rmtree(musica_path)
    except Exception as e:
        print(f"Erro ao apagar {videos_path}: {e}")

    if os.path.exists(video_final_path):
        try:
            os.remove(video_final_path)
            print("Arquivo video_final.mp4 apagado com sucesso.")
        except Exception as e:
            print(f"Erro ao apagar video_final.mp4: {e}")
    else:
        print("Arquivo video_final.mp4 não encontrado.")


if __name__ == "__main__":
    base_dir = (
        "C:\\Users\\rafae\\OneDrive\\Área de Trabalho\\YouTubeVideoGenerator\\bible"
    )
    delete_files(base_dir)
