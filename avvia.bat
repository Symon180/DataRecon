@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Crea prima il venv: vedi README
    exit /b 1
)
".venv\Scripts\python.exe" "CODICE\app.py" %*
