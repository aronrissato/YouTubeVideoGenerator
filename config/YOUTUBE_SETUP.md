# Configuração do YouTube para GitHub Actions

## Problema Resolvido

O código agora suporta **tokens em formato JSON** (compatível com GitHub Secrets) ao invés de apenas pickle binário.

## Como Gerar o Token do YouTube

### Passo 1: Execute o script localmente

```bash
python config/generate_youtube_token.py
```

### Passo 2: Autentique no navegador

O script abrirá seu navegador para você fazer login no YouTube e autorizar o aplicativo.

### Passo 3: Copie o token JSON

O script mostrará algo assim:

```json
{
  "token": "ya29.a0AQQ_BDS...",
  "refresh_token": "1//0g...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456...apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "scopes": [
    "https://www.googleapis.com/auth/youtube.upload"
  ]
}
```

**Copie TODO o conteúdo** (incluindo `{` e `}`)

### Passo 4: Configure o GitHub Secret

1. Vá para seu repositório no GitHub
2. Click em **Settings** → **Secrets and variables** → **Actions**
3. Encontre o secret `YOUTUBE_TOKEN`
4. Clique em **Update**
5. Cole o JSON completo que você copiou
6. Clique em **Update secret**

### Passo 5: Teste

Execute o workflow do GitHub Actions. Agora a autenticação do YouTube deve funcionar!

## Formato do Token

### ✅ Formato Correto (JSON):
```json
{
  "token": "...",
  "refresh_token": "...",
  ...
}
```

### ❌ Formato Incorreto (Pickle/String):
```
ASVBAQAAAAAAACMGWdvb2dsZS5vYXV0aDIuY3JlZGVudGlhbHOUjAtDcmVkZW50aWFsc5STlCmBlH2U...
```

## Compatibilidade

O código agora tenta:
1. **JSON primeiro** (novo formato, compatível com GitHub)
2. **Pickle como fallback** (formato antigo, para compatibilidade local)

Isso garante que funcione tanto localmente quanto no GitHub Actions!

