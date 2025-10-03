"""
Buscador de vídeos do Pexels baseado na duração do áudio
"""
import requests
import os
import tempfile
from typing import List, Dict

class PexelsVideoFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {
            'Authorization': api_key
        }
        self.videos_dir = 'pexels_videos'
        
        # Criar diretório se não existir
        if not os.path.exists(self.videos_dir):
            os.makedirs(self.videos_dir)
    
    def search_videos(self, query: str, duration: int, per_page: int = 15) -> List[Dict]:
        """
        Busca vídeos no Pexels com base na query e duração total necessária
        """
        try:
            # Calcular quantos vídeos precisamos (assumindo 30s por vídeo)
            videos_needed = (duration // 30) + 1
            
            params = {
                'query': query,
                'per_page': min(per_page, videos_needed * 2),  # Buscar mais para ter opções
                'min_duration': 10,
                'max_duration': 60
            }
            
            response = requests.get(f"{self.base_url}/search", 
                                  headers=self.headers, 
                                  params=params)
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get('videos', [])
                
                print(f"Encontrados {len(videos)} vídeos para '{query}'")
                return videos
            else:
                print(f"Erro na API do Pexels: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Erro ao buscar vídeos: {str(e)}")
            return []
    
    def download_video(self, video_url: str, filename: str) -> str:
        """
        Baixa um vídeo do Pexels
        """
        try:
            response = requests.get(video_url)
            if response.status_code == 200:
                file_path = os.path.join(self.videos_dir, f"{filename}.mp4")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return file_path
            else:
                print(f"Erro ao baixar vídeo: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao baixar vídeo: {str(e)}")
            return None
    
    def get_videos_for_duration(self, query: str, total_duration: int) -> List[str]:
        """
        Obtém vídeos suficientes para cobrir a duração total do áudio
        """
        videos = self.search_videos(query, total_duration)
        
        if not videos:
            print("Nenhum vídeo encontrado")
            return []
        
        downloaded_videos = []
        current_duration = 0
        video_index = 0
        
        while current_duration < total_duration and video_index < len(videos):
            video = videos[video_index]
            
            # Pegar a melhor qualidade disponível
            video_files = video.get('video_files', [])
            if not video_files:
                video_index += 1
                continue
            
            # Ordenar por qualidade (HD > SD)
            video_files.sort(key=lambda x: x.get('width', 0), reverse=True)
            best_video = video_files[0]
            
            video_url = best_video.get('link')
            if not video_url:
                video_index += 1
                continue
            
            # Baixar vídeo
            filename = f"video_{video_index + 1}"
            file_path = self.download_video(video_url, filename)
            
            if file_path:
                downloaded_videos.append(file_path)
                video_duration = video.get('duration', 30)
                current_duration += video_duration
                print(f"Baixado: {filename} (duração: {video_duration}s, total: {current_duration}s)")
            
            video_index += 1
        
        print(f"Total de vídeos baixados: {len(downloaded_videos)}")
        print(f"Duração total dos vídeos: {current_duration}s")
        
        return downloaded_videos
    
    def get_bible_related_queries(self, book_name: str) -> List[str]:
        """
        Retorna queries relacionadas ao livro bíblico para buscar vídeos
        """
        queries = [
            "bible study",
            "religious meditation",
            "peaceful nature",
            "spiritual landscape",
            "biblical scenery",
            "holy place",
            "serene environment",
            "divine light",
            "sacred space",
            "tranquil nature"
        ]
        
        # Adicionar queries específicas baseadas no livro
        if book_name.lower() in ['genesis', 'exodus']:
            queries.extend(['creation', 'desert landscape', 'mountain view'])
        elif book_name.lower() in ['psalms', 'proverbs']:
            queries.extend(['wisdom', 'contemplation', 'peaceful meditation'])
        elif book_name.lower() in ['matthew', 'mark', 'luke', 'john']:
            queries.extend(['jesus christ', 'gospel', 'catholic church'])
        elif book_name.lower() == 'revelation':
            queries.extend(['apocalypse', 'heavenly light', 'divine vision'])
        
        return queries

def main():
    # Exemplo de uso
    api_key = input("Digite sua API key do Pexels: ")
    fetcher = PexelsVideoFetcher(api_key)
    
    # Simular busca para 5 minutos de áudio
    duration = 300  # 5 minutos
    query = "bible study"
    
    videos = fetcher.get_videos_for_duration(query, duration)
    print(f"Vídeos baixados: {videos}")

if __name__ == "__main__":
    main()
