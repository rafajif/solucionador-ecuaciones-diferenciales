@echo off
setlocal EnableExtensions
title Instalacion de EDO Lab
cd /d "%~dp0"

echo ================================================
echo        Instalador local de EDO Lab
echo ================================================
echo.

set "PY_CMD="
where python >nul 2>&1
if not errorlevel 1 (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3"
  )
)
if not defined PY_CMD (
  echo ERROR: No se encontro Python 3.10 o posterior.
  echo Instala Python desde https://www.python.org/downloads/windows/
  echo Activa la opcion para agregar Python al PATH o instala el launcher py.
  goto :failed
)
echo Python detectado:
call %PY_CMD% --version

where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: No se encontro Node.js.
  echo Instala Node.js LTS desde https://nodejs.org/ y vuelve a ejecutar este archivo.
  goto :failed
)
node -e "const v=process.versions.node.split('.').map(Number);process.exit(v[0]>=20?0:1)" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Se requiere Node.js 20 o posterior. Version detectada:
  node --version
  echo Instala una version LTS reciente desde https://nodejs.org/.
  goto :failed
)
where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: No se encontro npm. Reinstala Node.js LTS incluyendo npm.
  goto :failed
)
echo Node.js y npm detectados:
node --version
call npm --version
echo.

if not exist ".venv\Scripts\python.exe" (
  echo [1/6] Creando entorno virtual de Python...
  call %PY_CMD% -m venv .venv
  if errorlevel 1 (echo ERROR: No se pudo crear .venv.& goto :failed)
) else (
  echo [1/6] Reutilizando el entorno virtual existente.
)

echo [2/6] Instalando dependencias locales del backend...
".venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
if errorlevel 1 (echo ERROR: Fallo la instalacion del backend. Comprueba Internet y vuelve a intentarlo.& goto :failed)

echo [3/6] Instalando dependencias del frontend...
pushd frontend
call npm install --no-audit --no-fund
if errorlevel 1 (popd& echo ERROR: Fallo npm install. Comprueba Internet y la version de Node.js.& goto :failed)

echo [4/6] Compilando la aplicacion React para produccion...
call npm run build
if errorlevel 1 (popd& echo ERROR: La compilacion de React fallo.& goto :failed)
popd

echo [5/6] Ejecutando las pruebas automatizadas de Python...
pushd backend
"..\.venv\Scripts\python.exe" -m pytest
if errorlevel 1 (popd& echo ERROR: Las pruebas fallaron. No se considera completada la instalacion.& goto :failed)
popd

echo [6/6] Comprobando archivos necesarios...
if not exist "frontend\dist\index.html" (echo ERROR: No se genero frontend\dist\index.html.& goto :failed)
if not exist ".venv\Scripts\python.exe" (echo ERROR: No existe el Python del entorno virtual.& goto :failed)

echo.
echo ================================================
echo Instalacion completada correctamente.
echo Ahora ejecuta iniciar.bat para abrir EDO Lab.
echo El uso normal funciona sin Internet.
echo ================================================
pause
exit /b 0

:failed
echo.
echo Instalacion incompleta. Corrige el problema indicado y vuelve a ejecutar instalar.bat.
pause
exit /b 1
