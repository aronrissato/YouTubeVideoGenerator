# YouTube Video Generator

Sistema automatizado para criação e publicação de vídeos no YouTube com legendas, narração e edição automática.

## 📁 Estrutura do Projeto

```
YouTubeVideoGenerator/
├── bible/          # Vídeos sobre capítulos bíblicos
├── cats/           # Vídeos sobre gatos
├── jesus/          # Vídeos sobre Jesus
├── common/         # Módulos compartilhados
└── requirements.txt
```

### Tipos de Vídeo

- **bible/**: Gera vídeos sobre capítulos bíblicos com narração em inglês
- **cats/**: Cria vídeos sobre gatos com conteúdo específico
- **jesus/**: Produz vídeos sobre Jesus com temas religiosos

Cada pasta de tema contém seu próprio `yt_video_maker.py` com configurações específicas.

## 🔑 Configuração de APIs

### 1. Pexels API (Vídeos)
- Acesse: https://www.pexels.com/api/
- Crie conta gratuita
- Obtenha sua chave de API

### 2. Google Gemini API (Texto)
- Acesse: https://makersuite.google.com/app/apikey
- Crie conta Google
- Obtenha sua chave de API

### 3. YouTube API (Upload)
- Acesse: https://console.developers.google.com/
- Ative a YouTube Data API v3
- Crie credenciais OAuth 2.0
- Baixe o arquivo `client_secret.json`

## ⚙️ Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na pasta do projeto desejado (ex: `bible/.env`):
```env
KEY_PEXELS=sua_chave_do_pexels
KEY_GEMINI=sua_chave_do_gemini
```

### 3. Adicionar Credenciais do YouTube
- Coloque o arquivo `client_secret.json` na pasta do projeto
- O arquivo `token.json` será criado automaticamente na primeira execução

## 🚀 Como Executar

```bash
cd bible  # ou cats, jesus
python yt_video_maker.py
```

## ⚙️ Personalização

### Configurações por Tema

Cada pasta de tema permite personalizar:

- **Termos de busca**: Para vídeos no Pexels
- **Idioma**: Da narração e legendas
- **Tags**: Para SEO no YouTube
- **Categoria**: Do vídeo no YouTube
- **Música**: De fundo do vídeo

### Exemplo de Configuração (bible/yt_video_maker.py)

```python
# Configurações de vídeo
SEARCH_QUERY = "christian"      # Termo de busca no Pexels
ORIENTATION = "landscape"       # Orientação do vídeo
VIDEOS_COUNT = "6"              # Quantidade de vídeos

# Configurações de conteúdo
IDIOMA = "inglês"               # Idioma da narração
SELECT_MODEL = "gemini-1.5-flash"  # Modelo do Gemini

# Configurações do YouTube
TAGS = ["angel messages", "bible verses", ...]  # Tags SEO
CATEGORY_ID = "22"              # Categoria (People & Blogs)
```

## 🔧 Funcionalidades

- **Download de vídeos**: Pexels API
- **Geração de texto**: Google Gemini AI
- **Narração**: Google Text-to-Speech
- **Legendas**: Whisper AI
- **Edição de vídeo**: MoviePy
- **Upload**: YouTube API
- **Limpeza automática**: Remove arquivos temporários em caso de erro

## 📋 Requisitos

- Python 3.11+
- Chaves de API (Pexels, Gemini, YouTube)
- Conexão com internet
- Espaço em disco para vídeos temporários

## 🔄 Fluxo de Execução

```
1. Carregar Configurações
   ├── Ler arquivo .env
   ├── Validar chaves de API
   └── Configurar parâmetros

2. Download de Vídeos
   ├── Buscar vídeos no Pexels
   ├── Baixar vídeos HD
   └── Salvar na pasta videos/

3. Geração de Conteúdo
   ├── Gerar texto com Gemini AI
   ├── Criar narração com TTS
   └── Gerar legendas com Whisper

4. Edição de Vídeo
   ├── Baixar música de fundo
   ├── Unificar vídeo + áudio
   └── Adicionar legendas

5. Publicação
   ├── Autenticar YouTube API
   ├── Fazer upload do vídeo
   ├── Adicionar legendas
   └── Configurar metadados

6. Limpeza
   ├── Remover arquivos temporários
   └── Finalizar processo
```

## 🛡️ Segurança

- Arquivos sensíveis protegidos pelo `.gitignore`
- Chaves de API não expostas no código
- Limpeza automática de arquivos temporários

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de chave de API**
   - Verifique se o arquivo `.env` existe
   - Confirme se as chaves estão corretas

2. **Erro de codificação do .env**
   - Recrie o arquivo `.env` com codificação UTF-8
   - Use um editor de texto simples

3. **Falha no upload do YouTube**
   - Ative a YouTube Data API v3 no Google Console
   - Verifique se o arquivo `client_secret.json` está correto

4. **Limpeza automática**
   - Em caso de erro, o sistema remove automaticamente:
     - Pasta `videos/`
     - Pasta `music/`
     - Arquivos temporários

### Logs e Debug

O sistema mostra logs detalhados de cada etapa:
```
[03-10-2025 02:01:53] - Getting videos
[03-10-2025 02:01:54] - Getting text and chapter for the speech using Gemini
[03-10-2025 02:01:55] - Getting music from YouTube
```
