@echo off
setlocal

if not exist .venv\Scripts\python.exe (
    echo [SlayerAI] Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 goto :erro
)

echo [SlayerAI] Atualizando pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :erro

echo [SlayerAI] Instalando dependencias do projeto...
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :erro

echo [SlayerAI] Instalando dependencias de desenvolvimento...
call .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto :erro

echo.
echo Ambiente de desenvolvimento preparado.
echo.
echo Testes:
echo   .venv\Scripts\python.exe -m pytest -q
echo.
echo Diagnostico:
echo   .venv\Scripts\python.exe src\diagnostico.py
goto :fim

:erro
echo.
echo Falha durante a preparacao do ambiente de desenvolvimento.
exit /b 1

:fim
endlocal
