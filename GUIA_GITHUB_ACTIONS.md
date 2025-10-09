# 🚀 Guia: Automação com GitHub Actions

Guia completo para automatizar a geração de vídeos bíblicos usando GitHub Actions (100% gratuito e automático).

---

## ✨ O que foi criado

### Arquivos novos:
1. **`run_automated.py`** - Script que escolhe livro aleatoriamente e gera vídeo
2. **`.github/workflows/generate-video.yml`** - Workflow do GitHub Actions (já configurado para automação)
3. **`GUIA_GITHUB_ACTIONS.md`** - Este guia

---

## 🎯 Como funciona (100% Automático)

```
1. GitHub Actions executa TODO DIA às 10:00 UTC (07:00 Brasília)
2. Script escolhe livro bíblico ALEATÓRIO (1-66)
3. Gera vídeo completo (até 8 horas de timeout)
4. Publica AUTOMATICAMENTE no YouTube
5. Limpa arquivos temporários
6. Fim! Zero interação necessária
```

---

## 🚀 Passo a Passo Completo

### **Passo 1: Adicionar Secrets no GitHub**

1. Vá no seu repositório no GitHub
2. Clique em **Settings** (configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**

#### Adicione estes secrets:

**Obrigatório:**
- Nome: `PEXELS_API_KEY`
- Valor: sua chave do Pexels (https://www.pexels.com/api/)

**Opcional (para melhor qualidade de voz):**
- Nome: `AZURE_SPEECH_KEY`
- Valor: sua chave do Azure Speech Services
- Nome: `AZURE_SPEECH_REGION`
- Valor: `eastus` (ou sua região)

**Opcional (para publicação automática no YouTube):**
- Nome: `YOUTUBE_CLIENT_SECRET`
- Valor: conteúdo do arquivo `config/client_secret.json`
- Nome: `YOUTUBE_TOKEN`
- Valor: conteúdo do arquivo `config/token.json`

---

### **Passo 2: Fazer Commit e Push**

O workflow já está configurado para executar automaticamente. Apenas faça:

```bash
git add .
git commit -m "Adicionar automação de vídeos"
git push
```

**Pronto!** O sistema já está funcionando e executará automaticamente todo dia às 10:00 UTC (07:00 Brasília).

---

### **Passo 3: Monitorar Primeira Execução**

Aguarde a primeira execução automática ou verifique execuções passadas:

1. No GitHub, vá em **Actions** (aba superior)
2. Veja o workflow **Generate Bible Video**
3. Clique em qualquer execução para ver logs em tempo real
4. O vídeo será publicado automaticamente no YouTube

---

## ⏰ Ajustar Horário de Execução

O workflow está configurado para executar **todo dia às 10:00 UTC (07:00 Brasília)**.

Para alterar o horário, edite a linha `cron` no arquivo `.github/workflows/generate-video.yml`:

### Exemplos (sempre em UTC):

```yaml
# Todo dia às 10:00 UTC (07:00 Brasília)
- cron: '0 10 * * *'

# Todo dia às 12:00 UTC (09:00 Brasília)
- cron: '0 12 * * *'

# Todo dia às 15:00 UTC (12:00 Brasília)
- cron: '0 15 * * *'

# Todo dia às 18:00 UTC (15:00 Brasília)
- cron: '0 18 * * *'

# Segunda a sexta às 14:00 UTC (11:00 Brasília)
- cron: '0 14 * * 1-5'

# Duas vezes por dia: 10h e 22h UTC (07h e 19h Brasília)
- cron: '0 10,22 * * *'
```

**⚠️ IMPORTANTE:** 
- Horários são sempre em **UTC** (horário de Greenwich)
- **Brasil = UTC - 3 horas**
- Exemplo: 10:00 UTC = 07:00 Brasília
- Calculadora: https://crontab.guru/

---

## 🎯 Seleção de Livro (Aleatório)

O sistema está configurado para escolher **aleatoriamente** um dos 66 livros da Bíblia a cada execução.

Isso garante variedade e completa toda a Bíblia em aproximadamente 66 dias (considerando alguns livros repetidos pelo sorteio aleatório).

**Funciona assim:**
- A cada execução, o script sorteia um número de 1 a 66
- Esse número corresponde a um livro bíblico
- O vídeo é gerado para aquele livro
- Próxima execução = novo sorteio

Se quiser testar localmente com livro específico:
```bash
python run_automated.py 1        # Genesis
python run_automated.py 19       # Salmos
python run_automated.py genesis  # Por nome
```

---

## 📊 Monitoramento

### Ver Execuções:
1. GitHub → **Actions**
2. Veja histórico de execuções
3. Clique em qualquer execução para ver logs

### Ver Vídeo Gerado:
1. Na execução bem-sucedida, vá em **Artifacts**
2. Baixe `generated-video-XXX`
3. O vídeo estará no arquivo .zip

### Verificar Erros:
- Se falhar, veja os logs no próprio GitHub Actions
- Artifacts também incluem logs de erro

---

## 📹 Publicação Automática no YouTube

### Configurar:

#### **Método 1: OAuth Token (Recomendado)**

1. Execute localmente uma vez:
```bash
python run.py
```

2. Faça login no YouTube quando solicitado

3. Dois arquivos serão criados na pasta `config/`:
   - `client_secret.json`
   - `token.json`

4. Adicione como secrets no GitHub:

**YOUTUBE_CLIENT_SECRET:**
```bash
# Copie todo conteúdo do arquivo
cat config/client_secret.json
```

**YOUTUBE_TOKEN:**
```bash
# Copie todo conteúdo do arquivo
cat config/token.json
```

5. No `video_config.json`, configure:
```json
{
  "youtube_settings": {
    "privacy": "public",
    "category": "22",
    "auto_publish": true
  }
}
```

6. Commit e push do `video_config.json`:
```bash
git add video_config.json
git commit -m "Ativar auto-publicação YouTube"
git push
```

---

## 🎛️ Configurações do Vídeo

Edite o arquivo `video_config.json`:

```json
{
  "subject": "livro-biblico",
  "duration": "auto",
  "language": "en",
  "voice_speed": 0.8,
  "voice_gender": "male",
  "voice_volume": 1.0,
  "video_quality": "medium",
  "background_music": true,
  "background_music_volume": 0.2,
  "video_style": "calm",
  "custom_queries": [],
  "youtube_settings": {
    "privacy": "public",
    "category": "22",
    "auto_publish": true
  }
}
```

**Opções principais:**

- `language`: `"en"`, `"pt"`, `"es"`, `"fr"`, etc.
- `voice_speed`: `0.5` a `3.0` (1.0 = normal)
- `voice_gender`: `"male"` ou `"female"`
- `video_quality`: `"low"` (720p), `"medium"` (1080p), `"high"` (4K)
- `privacy`: `"public"`, `"unlisted"`, `"private"`
- `auto_publish`: `true` ou `false`

---

## 💰 Custos e Limites

**GitHub Actions:**
- Repositório público: **Ilimitado e grátis** ✨
- Repositório privado: **2000 minutos/mês grátis**

**Estimativa de uso (seu caso):**
- 1 vídeo/dia com até 8 horas de processamento
- Vídeos longos (3+ horas de áudio) = 4-6 horas de processamento
- Vídeos curtos = 1-2 horas de processamento
- **Média estimada:** ~4 horas por vídeo = 120 horas/mês

**Recomendação:**
- Use **repositório público** = ilimitado e grátis
- Ou repositório privado se tiver GitHub Pro (3000 min/mês)

**Timeout configurado:** 8 horas (480 minutos) por execução

---

## 🐛 Troubleshooting

### Erro: "PEXELS_API_KEY not found"
- Verifique se adicionou o secret no GitHub
- Nome deve ser exatamente `PEXELS_API_KEY`

### Erro: Timeout
- Edite o workflow e aumente `timeout-minutes`:
```yaml
timeout-minutes: 120  # 2 horas
```

### Vídeo não foi publicado no YouTube
- Verifique se `auto_publish: true` no `video_config.json`
- Verifique se adicionou secrets do YouTube
- Veja logs para mensagens de erro

### Workflow não executa automaticamente
- Verifique se descomentou as linhas do `schedule`
- Aguarde o horário configurado
- GitHub Actions pode ter até 10 minutos de atraso

### Erro de permissão
- Vá em Settings → Actions → General
- Em "Workflow permissions", selecione "Read and write permissions"

---

## 📝 Checklist Final

### Setup Inicial (Obrigatório):
- [x] Arquivos criados (`run_automated.py`, workflow)
- [ ] Secret `PEXELS_API_KEY` adicionado no GitHub
- [ ] Secrets do YouTube adicionados (`YOUTUBE_CLIENT_SECRET`, `YOUTUBE_TOKEN`)
- [ ] Arquivo `video_config.json` configurado com `auto_publish: true`
- [ ] Commit e push dos arquivos
- [ ] Aguardar horário da primeira execução (10:00 UTC / 07:00 Brasília)

### Opcional:
- [ ] Secret `AZURE_SPEECH_KEY` (para vozes neurais de melhor qualidade)
- [ ] Secret `AZURE_SPEECH_REGION` (ex: eastus)
- [ ] Ajustar horário do cron se desejar

### Monitoramento:
- [ ] Verificar primeira execução no GitHub Actions
- [ ] Confirmar publicação automática no YouTube
- [ ] Monitorar execuções diárias
- [ ] Verificar se todos os 66 livros estão sendo cobertos ao longo do tempo

---

## 🎯 Lista de 66 Livros

Para referência, os 66 livros na ordem:

**Antigo Testamento (1-39):**
1. genesis, 2. exodus, 3. leviticus, 4. numbers, 5. deuteronomy
6. joshua, 7. judges, 8. ruth, 9. 1_samuel, 10. 2_samuel
11. 1_kings, 12. 2_kings, 13. 1_chronicles, 14. 2_chronicles, 15. ezra
16. nehemiah, 17. esther, 18. job, 19. psalms, 20. proverbs
21. ecclesiastes, 22. song_of_songs, 23. isaiah, 24. jeremiah, 25. lamentations
26. ezekiel, 27. daniel, 28. hosea, 29. joel, 30. amos
31. obadiah, 32. jonah, 33. micah, 34. nahum, 35. habakkuk
36. zephaniah, 37. haggai, 38. zechariah, 39. malachi

**Novo Testamento (40-66):**
40. matthew, 41. mark, 42. luke, 43. john, 44. acts
45. romans, 46. 1_corinthians, 47. 2_corinthians, 48. galatians, 49. ephesians
50. philippians, 51. colossians, 52. 1_thessalonians, 53. 2_thessalonians, 54. 1_timothy
55. 2_timothy, 56. titus, 57. philemon, 58. hebrews, 59. james
60. 1_peter, 61. 2_peter, 62. 1_john, 63. 2_john, 64. 3_john
65. jude, 66. revelation

---

## 🎬 Resultado Final

**Após configurar tudo:**

1. ✅ GitHub Actions executará automaticamente no horário
2. ✅ Escolherá um livro aleatório a cada execução
3. ✅ Gerará vídeo completo
4. ✅ Publicará no YouTube (se configurado)
5. ✅ Você receberá notificações por email (se ativado)
6. ✅ Logs ficam disponíveis no GitHub Actions

**Tudo automático. Zero intervenção manual!** 🎉

---

## 📞 Dúvidas Comuns

**P: E se o vídeo demorar mais de 8 horas para processar?**
R: O timeout está configurado para 8 horas. Se um vídeo ultrapassar isso, a execução será cancelada. Você pode aumentar editando `timeout-minutes` no workflow, mas lembre-se de deixar folga entre execuções diárias.

**P: O que acontece se der erro em uma execução?**
R: O GitHub Actions registra o erro nos logs. A próxima execução ocorrerá normalmente no dia seguinte. Você receberá email de notificação se configurado.

**P: Posso gerar múltiplos vídeos por dia?**
R: Sim! Adicione múltiplas linhas de cron no schedule:
```yaml
schedule:
  - cron: '0 10 * * *'   # 10h UTC (07h Brasília)
  - cron: '0 22 * * *'   # 22h UTC (19h Brasília)
```
Certifique-se de deixar pelo menos 12 horas entre execuções.

**P: Como sei qual livro foi gerado?**
R: Veja os logs no GitHub Actions. O início da execução mostra qual livro foi sorteado. Ou verifique o título do vídeo publicado no YouTube.

**P: E se sortear o mesmo livro duas vezes seguidas?**
R: É possível (sorteio aleatório). Mas estatisticamente, ao longo de 66 dias, a maioria dos livros será coberta. Se quiser sequencial em vez de aleatório, posso modificar o script.

**P: Os vídeos ficam salvos no GitHub?**
R: Não. Eles são publicados automaticamente no YouTube e depois os arquivos temporários são deletados. O GitHub guarda apenas os logs da execução.

**P: Preciso fazer alguma manutenção?**
R: Não! Uma vez configurado, o sistema roda sozinho indefinidamente. Apenas monitore se tudo está funcionando corretamente.

---

**Pronto! Seu sistema está automatizado.** 🚀

*Desenvolvido para compartilhar a Palavra de Deus com tecnologia* 🙏

