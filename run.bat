@echo off

if not exist .venv\Scripts\python.exe (
    echo Ambiente virtual nao encontrado.
    echo Execute setup.bat primeiro.
    exit /b 1
)

.venv\Scripts\python.exe src\slayerai.py
