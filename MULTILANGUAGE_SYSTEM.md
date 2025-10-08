# Sistema Multi-Idioma - YouTube Video Generator

## Visão Geral

O YouTube Video Generator agora possui um sistema completamente agnóstico ao idioma, permitindo gerar vídeos bíblicos em qualquer língua suportada sem necessidade de criar arquivos específicos para cada idioma.

## Arquitetura

### Componentes Principais

1. **`bible_data_creator.py`** - Criador genérico de dados bíblicos
   - Suporta 14+ idiomas
   - Cria arquivos JSON com metadados de idioma
   - Detecta automaticamente pontuação por idioma
   - Inclui estatísticas (capítulos, versículos, palavras)

2. **`text/bible_text_generator.py`** - Gerador de texto multi-idioma
   - APIs configuráveis por idioma
   - Filtro de livros por idioma
   - Métodos para alternar idiomas dinamicamente
   - Suporte a dados locais e APIs online

3. **`config/config.py`** - Sistema de configuração
   - Integração com BibleDataCreator e BibleTextGenerator
   - Validação de idiomas
   - Métodos helper para obter instâncias configuradas

4. **`video/bible_video_generator.py`** - Gerador de vídeos
   - Aceita parâmetro de idioma na inicialização
   - Propaga idioma para todos os componentes
   - Mantém compatibilidade com código existente

## Idiomas Suportados

| Código | Nome Completo          | Status |
|--------|------------------------|--------|
| `pt`   | Português (Brasil)     | ✓      |
| `pt-pt`| Português (Portugal)   | ✓      |
| `en`   | English (US)           | ✓      |
| `en-gb`| English (UK)           | ✓      |
| `es`   | Español                | ✓      |
| `fr`   | Français               | ✓      |
| `de`   | Deutsch                | ✓      |
| `it`   | Italiano               | ✓      |
| `ru`   | Русский                | ✓      |
| `zh`   | 中文                    | ✓      |
| `ja`   | 日本語                  | ✓      |
| `ko`   | 한국어                  | ✓      |
| `ar`   | العربية                | ✓      |
| `he`   | עברית                  | ✓      |

## Como Usar

### Criar Dados Bíblicos em Qualquer Idioma

```python
from bible_data_creator import BibleDataCreator

# Criar instância
creator = BibleDataCreator()

# Criar livro em português
chapter_texts_pt = {
    1: 'No princípio criou Deus os céus e a terra.',
    2: 'E assim foram acabados os céus e a terra.'
}
creator.create_bible_book('Gênesis', chapter_texts_pt, language='pt')

# Criar livro em inglês
chapter_texts_en = {
    1: 'In the beginning God created the heaven and the earth.',
    2: 'Thus the heavens and the earth were finished.'
}
creator.create_bible_book('Genesis', chapter_texts_en, language='en')

# Criar livro em espanhol
chapter_texts_es = {
    1: 'En el principio creó Dios los cielos y la tierra.',
    2: 'Fueron, pues, acabados los cielos y la tierra.'
}
creator.create_bible_book('Génesis', chapter_texts_es, language='es')
```

### Gerar Texto Bíblico em Idioma Específico

```python
from text.bible_text_generator import BibleTextGenerator

# Criar gerador para português
generator_pt = BibleTextGenerator(language='pt')
texto = generator_pt.get_full_book_text('genesis')

# Criar gerador para inglês
generator_en = BibleTextGenerator(language='en')
text = generator_en.get_full_book_text('genesis')

# Alternar idioma dinamicamente
generator = BibleTextGenerator(language='en')
generator.set_language('pt')  # Muda para português
```

### Gerar Vídeo em Idioma Específico

```python
from video.bible_video_generator import BibleVideoGenerator

# Criar gerador para inglês
generator_en = BibleVideoGenerator(language='en')
generator_en.generate_full_video('genesis', pexels_key, publish=False)

# Criar gerador para português
generator_pt = BibleVideoGenerator(language='pt')
generator_pt.generate_full_video('genesis', pexels_key, publish=False)
```

### Configurar Idioma Padrão

Edite `video_config.json`:

```json
{
  "language": "pt",
  "voice_speed": 1.0,
  "voice_gender": "female",
  ...
}
```

Ou use a interface de configuração:

```bash
python run.py config
```

## Estrutura de Arquivos JSON

Os arquivos bíblicos agora incluem informação de idioma:

```json
{
  "reference": "Genesis",
  "language": "en",
  "language_name": "English (US)",
  "verses": [
    {
      "chapter": 1,
      "verse": 1,
      "text": "In the beginning God created..."
    }
  ],
  "text": "Full text...",
  "metadata": {
    "chapter_count": 50,
    "verse_count": 1533,
    "character_count": 150000,
    "word_count": 25000
  }
}
```

## Filtros por Idioma

### Listar Livros Disponíveis em um Idioma

```python
generator = BibleTextGenerator()

# Apenas livros em inglês
books_en = generator.get_available_books(language_filter='en')

# Apenas livros em português
books_pt = generator.get_available_books(language_filter='pt')
```

### Listar Todos os Livros com Informação de Idioma

```python
creator = BibleDataCreator()
books = creator.list_available_books()

for book in books:
    print(f"{book['book_name']} - {book['language_name']}")
```

## Testes

Execute o script de teste completo:

```bash
python test_multilanguage.py
```

O script testa:
1. ✓ Criação de dados bíblicos em diferentes idiomas
2. ✓ Leitura e filtro de livros por idioma
3. ✓ Integração com sistema de configuração
4. ✓ Listagem e agrupamento por idioma

## Migração

### Arquivos Antigos

O arquivo `bible_english_creator.py` foi **removido** e substituído por `bible_data_creator.py`.

### Arquivos JSON Existentes

Arquivos JSON sem campo `language` serão tratados como idioma `unknown`. Para migrar:

```python
from bible_data_creator import BibleDataCreator
import json
import os

creator = BibleDataCreator()

# Para cada arquivo sem idioma
for filename in os.listdir('bible_data'):
    if filename.endswith('.json'):
        filepath = os.path.join('bible_data', filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Adicionar campo de idioma se não existir
        if 'language' not in data:
            data['language'] = 'en'  # ou o idioma apropriado
            data['language_name'] = 'English (US)'
            
            with open(filepath, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
```

## Vantagens do Novo Sistema

1. **Escalável** - Adicionar novo idioma é apenas configurar a API/dados
2. **Manutenível** - Um único código base para todos os idiomas
3. **Flexível** - Alterar idioma em tempo de execução
4. **Organizado** - Filtros automáticos por idioma
5. **Robusto** - Validação e metadados completos
6. **Documentado** - Cada componente tem documentação clara

## Adicionando Novo Idioma

Para adicionar suporte a um novo idioma:

1. **Adicionar à lista de idiomas suportados** em `bible_data_creator.py`:

```python
SUPPORTED_LANGUAGES = {
    # ... idiomas existentes ...
    'ko': '한국어',  # Coreano
}
```

2. **Configurar API** em `text/bible_text_generator.py`:

```python
BIBLE_APIS = {
    # ... APIs existentes ...
    'ko': {
        'name': 'Bible API (Korean)',
        'base_url': 'https://bible-api.com',
        'version': 'kor'
    }
}
```

3. **Criar dados bíblicos** usando `bible_data_creator.py`

4. **Configurar voz** para o novo idioma (se aplicável)

## Suporte e Contribuições

Para reportar problemas ou sugerir melhorias no sistema multi-idioma, abra uma issue no repositório do projeto.

## Changelog

### v2.0 - Sistema Multi-Idioma
- ✓ Criado `bible_data_creator.py` genérico
- ✓ Atualizado `bible_text_generator.py` com suporte multi-idioma
- ✓ Integrado sistema de idiomas com `config.py`
- ✓ Atualizado `bible_video_generator.py` para aceitar idioma
- ✓ Removido `bible_english_creator.py` obsoleto
- ✓ Adicionado script de testes `test_multilanguage.py`
- ✓ Suporte a 14+ idiomas

### v1.0 - Sistema Original
- Suporte apenas para inglês
- Arquivo específico `bible_english_creator.py`

