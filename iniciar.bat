@echo off
setlocal EnableExtensions
title EDO Lab - Servidor local
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo No se encuentra el entorno de Python. Ejecuta primero instalar.bat.
  pause
  exit /b 1
)
if not exist "frontend\dist\index.html" (
  echo No se encontro el frontend compilado. Ejecuta instalar.bat para compilarlo.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import fastapi,sympy,uvicorn" >nul 2>&1
if errorlevel 1 (
  echo Faltan dependencias del backend. Ejecuta instalar.bat con Internet disponible.
  pause
  exit /b 1
)

echo Iniciando EDO Lab. Se abrira el navegador cuando el servidor este listo.
echo Mantén esta ventana abierta. Presiona Ctrl+C para cerrar la aplicacion.
pushd backend
"..\.venv\Scripts\python.exe" -m app.run_local
set "APP_EXIT=%ERRORLEVEL%"
popd
if not "%APP_EXIT%"=="0" (
  echo El servidor finalizo con un error. Revisa el mensaje anterior.
  pause
  exit /b %APP_EXIT%
)
exit /b 0
