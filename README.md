# 🎬 Gerador de Vídeos Bíblicos

Um projeto Python para gerar vídeos completos de livros bíblicos com narração, vídeos de fundo do Pexels, legendas e publicação automática no YouTube.

## 🚀 Funcionalidades

- **Geração de Texto**: Obtém o texto completo de qualquer livro bíblico
- **Narração em Áudio**: Converte o texto em áudio usando gTTS
- **Busca de Vídeos**: Encontra vídeos relacionados no Pexels
- **Criação de Vídeo**: Combina áudio e vídeos em um MP4 final
- **Geração de Legendas**: Cria arquivos SRT e VTT
- **Publicação no YouTube**: Upload automático com metadados
- **⚙️ Sistema de Configuração**: Interface completa para personalizar todas as opções do vídeo

## 📋 Pré-requisitos

- Python 3.8+
- Conta no Pexels (para API key)
- Conta no YouTube (para publicação)
- Google Cloud Console (para YouTube API)

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd YouTubeVideoGenerator
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp env_example.txt .env
```

Edite o arquivo `.env` com suas chaves de API:
```env
OPENAI_API_KEY=sua_chave_openai
PEXELS_API_KEY=sua_chave_pexels
```

4. Configure a autenticação do YouTube:
   - Acesse o [Google Cloud Console](https://console.cloud.google.com/)
   - Crie um projeto e ative a YouTube Data API v3
   - Crie credenciais OAuth 2.0
   - Baixe o arquivo `client_secret.json` para a raiz do projeto

## 🎯 Como Usar

### Configuração Inicial

Primeiro, configure suas opções personalizadas:

```bash
python run.py config
```

Isso abrirá uma interface interativa onde você pode configurar:
- **Assunto do vídeo**: Livro completo, capítulo, versículo, etc.
- **Duração**: Automática ou personalizada (1-180 minutos)
- **Idioma**: Português, inglês, espanhol, francês, alemão, italiano
- **Velocidade da voz**: 0.5x a 3.0x
- **Gênero da voz**: Masculina ou feminina
- **Qualidade do vídeo**: 720p, 1080p, 4K
- **Estilo do vídeo**: Dinâmico, calmo, dramático
- **Música de fundo**: Ativar/desativar e ajustar volume
- **Estilo das legendas**: Clássico, moderno, minimalista
- **Configurações do YouTube**: Privacidade, categoria, auto-publicação

### Execução Básica

```bash
python run.py
```

Siga as instruções na tela para:
1. Escolher entre gerar vídeo, configurar opções ou ver ajuda
2. Selecionar um livro bíblico
3. O sistema usará suas configurações salvas

### Execução com Livro Específico

```bash
python run.py genesis
python run.py salmos
python run.py joao
```

### Comandos Disponíveis

```bash
python run.py                    # Execução interativa completa
python run.py [nome-do-livro]    # Gerar vídeo de um livro específico
python run.py config             # Abrir configurações
python run.py help               # Mostrar ajuda
```

### Execução Programática

```python
from bible_video_generator import BibleVideoGenerator

generator = BibleVideoGenerator()

# Gerar vídeo completo
video_path = generator.generate_full_video(
    book_name="genesis",
    pexels_api_key="sua_chave_pexels",
    publish_to_youtube=True
)
```

## 📁 Estrutura do Projeto

```
YouTubeVideoGenerator/
├── run.py                      # Script principal de execução
├── config.py                   # Sistema de configuração
├── config_ui.py                # Interface de configuração
├── bible_video_generator.py    # Gerador principal
├── bible_text_generator.py     # Geração de texto bíblico
├── audio_generator.py          # Conversão texto→áudio
├── pexels_video_fetcher.py     # Busca de vídeos
├── video_creator.py            # Criação do vídeo final
├── subtitle_generator.py       # Geração de legendas
├── youtube_publisher.py        # Publicação no YouTube
├── video_config.json           # Configurações salvas (gerado automaticamente)
├── video_config_example.json   # Exemplo de configuração
├── requirements.txt            # Dependências
└── env_example.txt            # Exemplo de variáveis
```

## 📚 Livros Disponíveis

O projeto suporta todos os 66 livros da Bíblia:

**Antigo Testamento:**
- Gênesis, Êxodo, Levítico, Números, Deuteronômio
- Josué, Juízes, Rute, 1-2 Samuel, 1-2 Reis
- 1-2 Crônicas, Esdras, Neemias, Ester, Jó
- Salmos, Provérbios, Eclesiastes, Cantares
- Isaías, Jeremias, Lamentações, Ezequiel, Daniel
- Oséias, Joel, Amós, Obadias, Jonas, Miquéias
- Naum, Habacuque, Sofonias, Ageu, Zacarias, Malaquias

**Novo Testamento:**
- Mateus, Marcos, Lucas, João, Atos
- Romanos, 1-2 Coríntios, Gálatas, Efésios, Filipenses
- Colossenses, 1-2 Tessalonicenses, 1-2 Timóteo
- Tito, Filemom, Hebreus, Tiago, 1-2 Pedro
- 1-3 João, Judas, Apocalipse

## ⚙️ Configurações

Edite `config.py` para personalizar:

```python
# Configurações de áudio
AUDIO_LANGUAGE = 'pt'      # Idioma da narração
AUDIO_SPEED = 1.0          # Velocidade do áudio

# Configurações de vídeo
PEXELS_VIDEO_DURATION = 30  # Duração por vídeo (segundos)
PEXELS_VIDEO_QUALITY = 'large'  # Qualidade dos vídeos

# Configurações de publicação
DEFAULT_PRIVACY_STATUS = 'private'  # Status da publicação
DEFAULT_CATEGORY_ID = '22'          # Categoria (People & Blogs)
```

## 📁 Arquivos Gerados

O processo cria os seguintes arquivos:

- `temp/`: Texto original do livro
- `audio/`: Arquivo de áudio (MP3)
- `pexels_videos/`: Vídeos baixados do Pexels
- `output/`: Vídeo final (MP4)
- `subtitles/`: Legendas (SRT e VTT)

## ⚙️ Sistema de Configuração

O projeto inclui um sistema completo de configuração que permite personalizar todas as opções do vídeo:

### Arquivo de Configuração

As configurações são salvas automaticamente em `video_config.json`:

```json
{
  "subject": "livro-biblico",
  "duration": "auto",
  "language": "pt",
  "voice_speed": 1.0,
  "voice_gender": "female",
  "video_quality": "high",
  "background_music": true,
  "background_music_volume": 0.3,
  "subtitle_style": "modern",
  "video_style": "calm",
  "custom_queries": ["nature", "peaceful landscape"],
  "youtube_settings": {
    "privacy": "private",
    "category": "22",
    "auto_publish": false
  }
}
```

### Opções de Configuração

#### Assunto do Vídeo
- `livro-biblico`: Livro Bíblico Completo
- `capitulo-biblico`: Capítulo Bíblico Específico
- `versiculo-especifico`: Versículo Específico
- `estudo-biblico`: Estudo Bíblico
- `devocional`: Devocional Diário
- `historia-biblica`: História Bíblica
- `salmos`: Salmos e Louvores
- `proverbios`: Provérbios de Sabedoria

#### Idiomas Disponíveis
- `pt`: Português (Brasil)
- `pt-pt`: Português (Portugal)
- `en`: English (US)
- `en-gb`: English (UK)
- `es`: Español
- `fr`: Français
- `de`: Deutsch
- `it`: Italiano

#### Qualidade de Vídeo
- `low`: Baixa (720p)
- `medium`: Média (1080p)
- `high`: Alta (1080p otimizada)

#### Estilo de Vídeo
- `dynamic`: Dinâmico (música e transições rápidas)
- `calm`: Calmo (música suave e transições lentas)
- `dramatic`: Dramático (efeitos sonoros e visuais marcantes)

#### Estilo de Legendas
- `classic`: Clássico (fonte serifada, fundo preto)
- `modern`: Moderno (fonte sans-serif, fundo transparente)
- `minimal`: Minimalista (fonte fina, sem fundo)

### Comandos de Configuração

```bash
# Abrir interface de configuração
python run.py config

# Ver configurações atuais
python run.py help
```

## 🧹 Sistema de Limpeza Automática

O projeto inclui um sistema inteligente de limpeza de arquivos temporários:

### Limpeza Automática
- **Após publicação**: Arquivos são automaticamente removidos após upload no YouTube
- **Em caso de erro**: Limpeza automática em qualquer falha durante o processo
- **Interrupção manual**: Limpeza quando o processo é interrompido (Ctrl+C)

### Limpeza Manual
Execute o script de limpeza para remover arquivos temporários:

```bash
# Limpeza geral (todos os arquivos temporários)
python cleanup.py

# Limpeza específica de um livro
python cleanup.py genesis
```

### Arquivos Removidos na Limpeza
- Textos gerados (`temp/*_text.txt`)
- Áudios de narração (`audio/*_audio.mp3`)
- Vídeos do Pexels (`pexels_videos/*.mp4`)
- Vídeo final (`output/*_final.mp4`)
- Legendas (`subtitles/*_subtitles.srt`)
- Música de fundo (`temp/background_music.mp3`)
- Arquivos temporários do MoviePy (`temp/temp-audio*`)

## 🔧 Solução de Problemas

### Erro de Autenticação YouTube
- Verifique se `client_secret.json` está na raiz
- Confirme se a YouTube API está ativada
- Execute o fluxo de autenticação novamente

### Erro na API do Pexels
- Verifique se a API key está correta
- Confirme se não excedeu o limite de requisições
- Teste com uma nova chave de API

### Problemas de Memória
- Para livros muito longos, o processo pode consumir muita RAM
- Considere dividir o livro em partes menores
- Feche outros aplicativos durante a geração

### Erro no gTTS
- Verifique sua conexão com a internet
- O gTTS pode ter limites de caracteres por requisição
- O script divide automaticamente textos longos

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🙏 Agradecimentos

- [Pexels](https://pexels.com) por fornecer vídeos gratuitos
- [Google Text-to-Speech](https://cloud.google.com/text-to-speech) para narração
- [MoviePy](https://zulko.github.io/moviepy/) para edição de vídeo
- [YouTube Data API](https://developers.google.com/youtube/v3) para publicação

## 📞 Suporte

Se encontrar problemas ou tiver dúvidas:
1. Verifique a seção de solução de problemas
2. Consulte os logs de erro
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ para compartilhar a Palavra de Deus**
