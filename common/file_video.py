import requests
import random
import os


def get_video(key_pexels, download_folder, search_query, videos_count, orientation):
    os.makedirs(download_folder, exist_ok=True)
    headers = {"Authorization": key_pexels}
    pages = random.randint(1, 2)  # diff pages to search

    for page in range(1, pages + 1):
        url = f"https://api.pexels.com/videos/search?query={search_query}&per_page={videos_count}&page={page}&orientation={orientation}"
        resposta = requests.get(url, headers=headers)
        dados = resposta.json()
        
        if resposta.status_code != 200:
            print(f"Error: API returned status {resposta.status_code}")
            if resposta.status_code == 401:
                print("Error: Invalid API key. Please check your Pexels API key in .env file")
            return
            
        if "videos" not in dados:
            print(f"Error: 'videos' key not found in response. Available keys: {list(dados.keys())}")
            return

        for video in dados["videos"]:
            video_url = video["video_files"][0]["link"]
            video_id = video["id"]
            caminho = os.path.join(download_folder, f"{video_id}.mp4")

            print(f"Baixando: {video_url}")
            video_bin = requests.get(video_url).content
            with open(caminho, "wb") as f:
                f.write(video_bin)


if __name__ == "__main__":
    key_pexels = ""
    download_folder = "videos"
    search_query = "cats"
    orientation = "landscape"
    videos_count = "2"
    get_video(key_pexels, download_folder, search_query, videos_count, orientation)
