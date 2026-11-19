# EDO Lab

Aplicación educativa local para clasificar y resolver un subconjunto explícito de ecuaciones diferenciales ordinarias, con procedimientos simbólicos y verificación residual. No emplea servicios externos ni modelos generativos.

## Arquitectura

- `backend/app/safe_math.py`: parser restringido basado en el árbol sintáctico de Python; solo admite números, `x`, `y`, operaciones aritméticas y una lista corta de funciones.
- `backend/app/engine.py`: clasificación y procedimientos para ecuaciones lineales, exactas, homogéneas y un subconjunto autónomo reducible a Bernoulli.
- `backend/app/main.py`: API FastAPI local (`127.0.0.1:8000`).
- `frontend/`: React, TypeScript, Vite, Tailwind CSS, MathLive, KaTeX y Lucide.
- `backend/tests/`: pruebas unitarias iniciales para las familias y ejercicios indicados en el encargo.

La prioridad de clasificación es: segundo orden que pase la prueba reducida; luego, para `y'=F(x,y)`, homogeneidad antes que linealidad; finalmente la forma lineal estándar `y'+P(x)y=Q(x)`. Una ecuación explícita puede pertenecer a varias familias y se devuelve la lista de compatibilidades. Exactitud requiere los campos M y N y se activa en modo guiado.

## Requisitos e instalación

Se necesita Python 3.10 o posterior (recomendado 3.12) y Node.js 20 o posterior. La primera instalación requiere tener disponibles los paquetes indicados. Para preparar una máquina sin conexión, descargar/copiar previamente un wheelhouse de Python compatible y una copia de los paquetes npm; una vez preparados, el uso y el cálculo no requieren Internet.

### Backend (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app
```

API: `http://127.0.0.1:8000`; documentación local: `/docs`.

### Frontend (otra terminal)

```powershell
cd frontend
npm install
npm run dev
```

Abra la dirección local que imprime Vite, por defecto `http://127.0.0.1:5173`.

Para ejecutar totalmente desconectado después de preparar las dependencias, use `python -m pip install --no-index --find-links <wheelhouse> -r requirements.txt` y `npm install --offline` con caché npm previamente poblada.

## Uso y ejemplos

- Automático: `y'+3*y=9`, condición inicial `x₀=0`, `y₀=2`.
- Homogénea: `y'=(2*x+y)/x`.
- Modo guiado exacta: `M=4*x*y+2`, `N=2*x^2+6*y`.
- Orden dos: `y''+y'=(y')^2`, con `x₀=0`, `y₀=0`, `y′(x₀)=1`.

La API recibe LaTeX de MathLive solo en el subconjunto convertido al parser seguro. Los argumentos de funciones se limitan a `sin`, `cos`, `tan`, `exp`, `log`, `sqrt` y `Abs`. No se evalúa código Python.

## Pruebas

```powershell
cd backend
python -m pytest
```

## Limitaciones conocidas

- La detección y solución no son universales. La forma exacta se ofrece como modo guiado, no como inferencia fiable desde una expresión de texto arbitraria.
- En segundo orden se implementa el caso autónomo `p'=A*p+B*p^n`, con A y B constantes, que permite aplicar `p=y'` y la transformación de Bernoulli. Se conservan explícitamente los equilibrios y se selecciona la rama que satisface la pendiente inicial. Otros modelos se rechazan.
- El verificador prueba residuos exactos en las familias implementadas. Una simplificación que SymPy no demuestre se marca como indeterminada, no como correcta.
- El editor y el servicio se comunican como texto matemático validado, no mediante un AST compartido. El modo exacta usa campos algebraicos de texto y por ahora no tiene editor MathLive dedicado.
- Se limita tamaño y operaciones del parser; aún no hay aislamiento por proceso ni límite duro de tiempo para una integración simbólica patológica. Usar solo con entradas locales de confianza y mantener `127.0.0.1`.
- No hay PDF de referencia en el repositorio, así que no se pudo cotejar con el documento original. Los siete ejercicios descritos en el prompt se reflejan en las pruebas, pero las pruebas aún no se ejecutaron porque Python y Node/npm no están disponibles en la terminal de esta máquina.

## Dependencias

Backend: FastAPI, Uvicorn, SymPy, Pydantic y pytest. Frontend: React, Vite, TypeScript, Tailwind CSS, MathLive, KaTeX y Lucide React. No se utilizan NumPy, SciPy ni servicios remotos.
