@echo off
setlocal

echo [SlayerAI] Criando ambiente virtual...
python -m venv .venv
if errorlevel 1 goto :erro

echo [SlayerAI] Atualizando pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :erro

echo [SlayerAI] Instalando dependencias...
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :erro

echo.
echo Ambiente preparado com sucesso.
echo Rode:
echo   .venv\Scripts\python.exe src\diagnostico.py
echo   .venv\Scripts\python.exe src\slayerai.py
goto :fim

:erro
echo.
echo Falha durante a preparacao do ambiente.
exit /b 1

:fim
endlocal
