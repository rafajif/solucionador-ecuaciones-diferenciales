@echo off
setlocal EnableExtensions
title Preparar version portable de EDO Lab
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Ejecuta instalar.bat primero para instalar las dependencias y compilar el frontend.
  pause
  exit /b 1
)
if not exist "frontend\dist\index.html" (
  echo No se encontro frontend\dist\index.html. Ejecuta instalar.bat primero.
  pause
  exit /b 1
)
if exist "build\portable\EDOLab\EDOLab.exe" (
  echo Ya existe build\portable\EDOLab\EDOLab.exe.
  echo Mueve la carpeta build\portable a otra ubicacion antes de crear otra compilacion.
  pause
  exit /b 1
)

echo Instalando PyInstaller en el entorno virtual del proyecto...
".venv\Scripts\python.exe" -m pip install "pyinstaller>=6,<7"
if errorlevel 1 (echo No se pudo instalar PyInstaller. Comprueba Internet.& pause& exit /b 1)

echo Creando el paquete portable de Windows. Puede tardar varios minutos.
".venv\Scripts\pyinstaller.exe" --noconfirm --clean --distpath "build\portable" --workpath "build\pyinstaller" "portable.spec"
if errorlevel 1 (echo PyInstaller fallo. No se ha creado un ejecutable validado.& pause& exit /b 1)
if not exist "build\portable\EDOLab\EDOLab.exe" (echo No se genero el ejecutable esperado.& pause& exit /b 1)

echo.
echo Paquete generado en build\portable\EDOLab\EDOLab.exe
echo Copia la carpeta completa EDOLab para distribuirla. El ejecutable aun debe probarse en el equipo destino.
pause
exit /b 0
