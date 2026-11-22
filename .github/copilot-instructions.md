# Instrucciones del repositorio EDO Lab

## Descripción general del repositorio

EDO Lab es una aplicación local para Windows que permite clasificar y resolver un conjunto limitado de ecuaciones diferenciales ordinarias. El entorno de ejecución habitual utiliza FastAPI + Uvicorn junto con un frontend de React/Vite compilado; ambos se sirven desde FastAPI en `127.0.0.1:8000`.

- `backend/app/main.py` define la aplicación FastAPI, los endpoints `/api/health`, `/api/identificar`, `/api/resolver` y monta `frontend/dist` como contenido estático del mismo origen.
- `backend/app/engine.py` contiene la lógica de clasificación y resolución mediante SymPy. Las familias compatibles son: ecuaciones lineales de primer orden, homogéneas, exactas y una reducción limitada de Bernoulli autónoma de segundo orden.
- `backend/app/safe_math.py` convierte el subconjunto de LaTeX de MathLive y analiza expresiones mediante una lista estricta de elementos permitidos en el AST de Python. Este es el límite de seguridad: no se utiliza evaluación arbitraria de Python.
- `backend/app/run_local.py` administra el servidor local en primer plano, el bloqueo para evitar múltiples instancias y el inicio del navegador.
- `backend/run_app.py` es el punto de entrada para la versión compilada mediante PyInstaller.
- `frontend/src/App.tsx` contiene la interfaz de React, el editor MathLive, las llamadas a la API, el historial local, la representación con KaTeX y la presentación de las respuestas.
- `frontend/build.mjs` compila Vite mediante una llamada directa al proceso de compilación, ya que la compilación de producción no necesita intencionalmente el proxy de Vite.
- `portable.spec` empaqueta el backend y el frontend compilado con PyInstaller en una distribución de Windows de tipo carpeta independiente.

## Configuración e instalación y comandos habituales

Requisitos previos: Python 3.10 o superior (se recomienda Python 3.12) y Node.js 20 o superior.

El procedimiento de instalación compatible con Windows utiliza los archivos por lotes de la raíz del proyecto:

```bat
instalar.bat
iniciar.bat