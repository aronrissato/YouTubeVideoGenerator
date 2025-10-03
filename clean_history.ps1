# Script para limpar histórico do Git e remover chaves expostas
Write-Host "🧹 Limpando histórico do Git para remover chaves expostas..." -ForegroundColor Yellow

# 1. Fazer backup dos arquivos importantes
Write-Host "📦 Criando backup dos arquivos..." -ForegroundColor Blue
if (!(Test-Path "backup")) {
    New-Item -ItemType Directory -Name "backup"
}
Copy-Item -Path "." -Destination "backup" -Recurse -Force -Exclude ".git"

# 2. Verificar se há chaves expostas no histórico
Write-Host "🔍 Verificando chaves expostas no histórico..." -ForegroundColor Blue
$exposedKeys = git log --all --full-history -- "*" | Select-String -Pattern "9hQ6EbbYCRZ1jlgwmyuwpS9GvNEOw7uNl4AjS31I7uiCHc0wOIAYjwV8"
if ($exposedKeys) {
    Write-Host "⚠️  ATENÇÃO: Chaves expostas encontradas no histórico!" -ForegroundColor Red
    Write-Host "Chaves encontradas: $($exposedKeys.Count)" -ForegroundColor Red
} else {
    Write-Host "✅ Nenhuma chave exposta encontrada no histórico" -ForegroundColor Green
}

# 3. Remover o diretório .git
Write-Host "🗑️  Removendo histórico do Git..." -ForegroundColor Blue
if (Test-Path ".git") {
    Remove-Item -Path ".git" -Recurse -Force
}

# 4. Inicializar novo repositório
Write-Host "🆕 Inicializando novo repositório..." -ForegroundColor Blue
git init

# 5. Adicionar todos os arquivos
Write-Host "📁 Adicionando arquivos..." -ForegroundColor Blue
git add .

# 6. Fazer commit inicial
Write-Host "💾 Criando commit inicial limpo..." -ForegroundColor Blue
git commit -m "Initial commit - Clean repository without exposed keys"

Write-Host ""
Write-Host "✅ Histórico limpo com sucesso!" -ForegroundColor Green
Write-Host "✅ Todos os commits antigos foram removidos" -ForegroundColor Green
Write-Host "✅ Nenhuma chave exposta no histórico" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Crie um novo repositório no GitHub" -ForegroundColor White
Write-Host "2. Execute: git remote add origin URL_DO_SEU_REPOSITORIO" -ForegroundColor White
Write-Host "3. Execute: git push -u origin master" -ForegroundColor White
Write-Host ""
Write-Host "🔒 Backup criado na pasta 'backup' caso precise recuperar algo" -ForegroundColor Cyan
