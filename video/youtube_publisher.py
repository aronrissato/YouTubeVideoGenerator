"""
Publicador de vídeos no YouTube
"""
import os
import pickle
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubePublisher:
    def __init__(self, client_secret_file='config/client_secret.json', token_file='config/token.json'):
        self.client_secret_file = client_secret_file
        self.token_file = token_file
        self.youtube = None
        self.credentials = None
        
        # Scopes necessários para YouTube API
        self.SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
    
    def authenticate(self):
        """
        Autentica com a API do YouTube
        """
        try:
            # Carregar credenciais existentes
            if os.path.exists(self.token_file):
                # Tentar carregar como JSON primeiro (mais seguro e compatível com GitHub secrets)
                try:
                    with open(self.token_file, 'r') as token:
                        token_data = json.load(token)
                        self.credentials = Credentials.from_authorized_user_info(token_data, self.SCOPES)
                except (json.JSONDecodeError, ValueError):
                    # Fallback para formato pickle (compatibilidade com versões antigas)
                    try:
                        with open(self.token_file, 'rb') as token:
                            self.credentials = pickle.load(token)
                    except Exception as pickle_error:
                        print(f"Erro ao carregar token (JSON e pickle falharam): {str(pickle_error)}")
                        self.credentials = None
            
            # Se não há credenciais válidas, fazer login
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        # Tentar renovar o token
                        self.credentials.refresh(Request())
                    except Exception as refresh_error:
                        error_str = str(refresh_error)
                        
                        # Verificar se é erro de token expirado/revogado
                        if 'invalid_grant' in error_str.lower() or 'token has been expired or revoked' in error_str.lower():
                            print("\n" + "="*70)
                            print("ERRO: Token do YouTube expirou ou foi revogado!")
                            print("="*70)
                            print("\nO token precisa ser regenerado manualmente.")
                            print("\nPara resolver este problema:")
                            print("1. Execute localmente: python config/generate_youtube_token.py")
                            print("2. Siga as instruções para autenticar no YouTube")
                            print("3. Copie o novo token gerado para o GitHub Secret YOUTUBE_TOKEN")
                            print("\nOBS: Tokens do YouTube expiram após ~6 meses de inatividade")
                            print("ou quando o acesso é revogado manualmente.")
                            print("="*70 + "\n")
                            
                            # Remover token inválido
                            if os.path.exists(self.token_file):
                                try:
                                    os.remove(self.token_file)
                                    print(f"Token inválido removido: {self.token_file}")
                                except:
                                    pass
                            
                            return False
                        else:
                            # Outro tipo de erro
                            print(f"Erro ao renovar token: {error_str}")
                            raise
                else:
                    if not os.path.exists(self.client_secret_file):
                        print(f"Arquivo {self.client_secret_file} não encontrado!")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secret_file, self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Salvar credenciais para próximo uso (em JSON para compatibilidade)
                token_data = {
                    'token': self.credentials.token,
                    'refresh_token': self.credentials.refresh_token,
                    'token_uri': self.credentials.token_uri,
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'scopes': self.credentials.scopes
                }
                with open(self.token_file, 'w') as token:
                    json.dump(token_data, token, indent=2)
            
            # Construir serviço YouTube
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"Erro na autenticação: {str(e)}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: list = None, category_id: str = '22', 
                    privacy_status: str = 'private') -> str:
        """
        Faz upload de vídeo para o YouTube
        """
        try:
            if not self.youtube:
                if not self.authenticate():
                    return None
            
            # Preparar metadados do vídeo
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            
            # Criar objeto de mídia
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            # Iniciar upload
            print(f"Iniciando upload: {title}")
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Executar upload
            response = request.execute()
            video_id = response['id']
            
            print(f"Upload concluído! ID do vídeo: {video_id}")
            print(f"URL do vídeo: https://www.youtube.com/watch?v={video_id}")
            
            return video_id
            
        except Exception as e:
            print(f"Erro no upload: {str(e)}")
            return None
    
    def update_video_metadata(self, video_id: str, title: str = None, 
                             description: str = None, tags: list = None) -> bool:
        """
        Atualiza metadados de um vídeo existente
        """
        try:
            if not self.youtube:
                if not self.authenticate():
                    return False
            
            # Buscar vídeo existente
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                print("Vídeo não encontrado")
                return False
            
            video = video_response['items'][0]
            snippet = video['snippet']
            
            # Atualizar campos se fornecidos
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags
            
            # Atualizar vídeo
            update_response = self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            print("Metadados atualizados com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar metadados: {str(e)}")
            return False
    
    def get_video_info(self, video_id: str) -> dict:
        """
        Obtém informações de um vídeo
        """
        try:
            if not self.youtube:
                if not self.authenticate():
                    return {}
            
            response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if response['items']:
                return response['items'][0]
            return {}
            
        except Exception as e:
            print(f"Erro ao obter informações do vídeo: {str(e)}")
            return {}

def main():
    # Exemplo de uso
    publisher = YouTubePublisher()
    
    # Autenticar
    if publisher.authenticate():
        # Exemplo de upload
        video_path = "output/video_final.mp4"
        title = "Livro de Gênesis - Narração Completa"
        description = "Narração completa do livro de Gênesis da Bíblia Sagrada."
        tags = ["bíblia", "genesis", "narração", "religião", "cristianismo"]
        
        if os.path.exists(video_path):
            video_id = publisher.upload_video(video_path, title, description, tags)
        else:
            print(f"Arquivo de vídeo não encontrado: {video_path}")

if __name__ == "__main__":
    main()
