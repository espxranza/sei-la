@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1
if "%ESTACAO_API_KEY%"=="" (
  echo.
  echo Defina a chave antes de executar:
  echo set ESTACAO_API_KEY=SUA_CHAVE
  echo.
  pause
  exit /b 1
)
python capturar_estacao.py
pause
