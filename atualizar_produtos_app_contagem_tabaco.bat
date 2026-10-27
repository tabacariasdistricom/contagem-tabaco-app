@echo off
rem Atualiza o catálogo de artigos da app de contagem de tabaco e publica.
rem  1) extrair_artigos.py (projeto zonsoft, só leitura, incremental)  2) gerar_artigos.py -> artigos.json
rem     e gerar_funcionarias.py -> funcionarias.json (se existir o Funcionarias.xlsx)
rem  3) sobe a VERSAO do sw.js  4) commit + push (GitHub Pages), depois de perguntar.
chcp 65001 >nul
cd /d "%~dp0"
title Atualizar produtos da app de contagem de tabaco

set "PY=C:\Users\Backoffice 01\OneDrive\meu\python\venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo.
echo [1/4] A atualizar os artigos a partir do ZoneSoft (so leitura)...
pushd "%~dp0..\zonsoft"
"%PY%" extrair_artigos.py
set "ERRO=%errorlevel%"
popd
if not "%ERRO%"=="0" echo ERRO ao extrair os artigos. Nada foi alterado.& pause & exit /b 1

echo.
echo [2/4] A gerar o catalogo da app (artigos.json) e a lista de funcionarias...
"%PY%" gerar_artigos.py
if errorlevel 1 echo ERRO ao gerar o catalogo.& pause & exit /b 1
if exist "Funcionarias.xlsx" "%PY%" gerar_funcionarias.py
if errorlevel 1 echo ERRO ao gerar a lista de funcionarias.& pause & exit /b 1

git add -N funcionarias.json >nul 2>&1
git diff --quiet -- artigos.json funcionarias.json
if not errorlevel 1 echo.& echo O catalogo e a lista de funcionarias nao mudaram. Nao ha nada para publicar.& pause & exit /b 0

echo.
echo Mudou:
git diff --stat -- artigos.json funcionarias.json
echo.
set /p OK=Publicar agora na app? (S/N): 
if /i not "%OK%"=="S" echo Nao publicado. Os ficheiros novos ficam so nesta pasta.& pause & exit /b 0

echo.
echo [3/4] A subir a versao do service worker...
"%PY%" subir_versao.py
if errorlevel 1 echo ERRO ao subir a versao.& pause & exit /b 1

echo.
echo [4/4] A publicar no GitHub...
git add artigos.json funcionarias.json sw.js
git -c user.name=ruifojocaetano -c user.email=334929231+ruifojocaetano@users.noreply.github.com commit -m "Catalogo e funcionarias atualizados (%date%)"
git push
if errorlevel 1 echo ERRO ao publicar. Verifica a ligacao e volta a correr.& pause & exit /b 1

echo.
echo Publicado. Dentro de cerca de 1 minuto a app ja tem o catalogo novo.
pause
