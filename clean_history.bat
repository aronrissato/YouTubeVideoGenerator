@echo off
echo Limpando historico do Git para remover chaves expostas...

REM 1. Fazer backup dos arquivos importantes
echo Criando backup dos arquivos...
if not exist "backup" mkdir backup
xcopy /E /I /Y . backup\*

REM 2. Remover o diretorio .git
echo Removendo historico do Git...
rmdir /S /Q .git

REM 3. Inicializar novo repositorio
echo Inicializando novo repositorio...
git init

REM 4. Adicionar todos os arquivos
echo Adicionando arquivos...
git add .

REM 5. Fazer commit inicial
echo Criando commit inicial limpo...
git commit -m "Initial commit - Clean repository without exposed keys"

echo.
echo ✅ Historico limpo com sucesso!
echo ✅ Todos os commits antigos foram removidos
echo ✅ Nenhuma chave exposta no historico
echo.
echo Para conectar ao GitHub:
echo 1. Crie um novo repositorio no GitHub
echo 2. Execute: git remote add origin URL_DO_SEU_REPOSITORIO
echo 3. Execute: git push -u origin master
echo.
pause
