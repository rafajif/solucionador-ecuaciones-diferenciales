# EDO Lab — Laboratorio de Ecuaciones Diferenciales Ordinarias

> **Documento de Instrucciones de Instalación y Ejecución**  
> **Destinatario:** Licenciado Hernán Antonio Berríos Gómez  
> **Proyecto:** EDO Lab — Aplicación local para la clasificación, resolución y verificación simbólica de Ecuaciones Diferenciales Ordinarias (EDO).

---

## 1. Presentación del Proyecto

Estimado **Licenciado Hernán Antonio Berríos Gómez**:

**EDO Lab** es una herramienta educativa y de cálculo simbólico diseñada para ejecutarse de forma **100% local en su equipo Windows**, sin depender de servicios en la nube ni de modelos generativos externos. La aplicación cuenta con una interfaz web moderna e interactiva desarrollada en **React** con soporte para notación matemática mediante **MathLive / KaTeX**, conectada a un núcleo de cálculo algebraico exacto en **Python (FastAPI + SymPy)**.

El sistema permite clasificar, resolver paso a paso y verificar el residuo de:
1. **Ecuaciones diferenciales lineales de primer orden:** $y' + P(x)y = Q(x)$.
2. **Ecuaciones homogéneas:** $y' = F(x, y)$ donde $F(tx, ty) = F(x, y)$.
3. **Ecuaciones diferenciales exactas:** $M(x, y)\,dx + N(x, y)\,dy = 0$ (modo guiado y detección).
4. **Ecuaciones de segundo orden reducibles:** familia autónoma $p' = A\,p + B\,p^n$ mediante la sustitución $p = y'$ y reducción a Bernoulli.

---

## 2. Requisitos Previos del Sistema

Para instalar y ejecutar EDO Lab por primera vez en su equipo con **Windows 10 o Windows 11**, se requieren los siguientes dos componentes instalados:

1. **Python 3.10 o superior** (se recomienda Python 3.11 o 3.12):
   - Descarga oficial: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
   - > [!IMPORTANT]
     > Al ejecutar el instalador de Python, asegúrese de marcar la casilla inferior que dice:  
     > **☑ "Add python.exe to PATH"** (o "Agregar Python al PATH"). Esto es indispensable para que los scripts por lotes reconozcan el comando `python`.

2. **Node.js 20 LTS o superior** (incluye `npm`):
   - Descarga oficial: [https://nodejs.org/](https://nodejs.org/) (descargar la versión recomendada para la mayoría / LTS).
   - El instalador configura automáticamente las variables de entorno necesarias.

> [!NOTE]
> **Sobre la conexión a Internet:**  
> La conexión a Internet solo es necesaria **una única vez** durante la ejecución del instalador (`instalar.bat`), para descargar las librerías oficiales de Python y Node.js. Una vez instalado, **el uso normal de la aplicación es completamente offline** y no requiere conexión.

---

## 3. Instrucciones de Instalación y Uso Rápido (Método Recomendado)

Se han preparado scripts automatizados para que no tenga que escribir comandos en la terminal.

### Paso 1: Instalación inicial (Se realiza solo una vez)

1. Abra la carpeta raíz del proyecto en el Explorador de Archivos de Windows.
2. Haga **doble clic** sobre el archivo [instalar.bat](file:///c:/Users/Dell_E7270/Desktop/Programa/instalar.bat).
3. Se abrirá una ventana de consola donde el asistente realizará automáticamente los 6 pasos requeridos:
   - **[1/6]** Creación del entorno virtual aislado de Python (`.venv`).
   - **[2/6]** Instalación de dependencias del backend (`FastAPI`, `Uvicorn`, `SymPy`, `Pydantic`, etc.).
   - **[3/6]** Descarga e instalación de dependencias del frontend (`React`, `MathLive`, `Tailwind CSS`).
   - **[4/6]** Compilación de la aplicación React para producción (`frontend/dist`).
   - **[5/6]** Ejecución de la batería de pruebas unitarias automatizadas (`pytest`).
   - **[6/6]** Verificación de integridad de los archivos generados.
4. Cuando el proceso finalice correctamente, verá el mensaje:
   ```text
   ================================================
   Instalacion completada correctamente.
   Ahora ejecuta iniciar.bat para abrir EDO Lab.
   ================================================
   ```
5. Presione cualquier tecla para cerrar la ventana del instalador.

---

### Paso 2: Iniciar la aplicación

1. En la misma carpeta raíz, haga **doble clic** sobre el archivo [iniciar.bat](file:///c:/Users/Dell_E7270/Desktop/Programa/iniciar.bat).
2. El script iniciará el servidor local en segundo plano e **inmediatamente abrirá su navegador web predeterminado** apuntando a la dirección local:
   $$\text{http://127.0.0.1:8000}$$
3. Ya puede interactuar libremente con **EDO Lab**, ingresar ecuaciones y explorar los procedimientos de resolución.

> [!TIP]
> **Para cerrar la aplicación:**  
> Mantenga la ventana negra de la consola abierta mientras utilice la aplicación. Cuando desee finalizar, vaya a dicha ventana de consola y presione la combinación de teclas `Ctrl + C` (o simplemente cierre la ventana). Esto apagará el servidor y liberará el puerto de red.

---

## 4. Instrucciones de Ejecución Manual (Vía Terminal)

Si el Licenciado prefiere inspeccionar los procesos o ejecutar los servicios manualmente mediante **PowerShell** o **Símbolo del sistema (CMD)**, puede seguir los siguientes pasos:

### 4.1 Preparación del Backend (Python)

Abra una ventana de PowerShell en la carpeta raíz del proyecto:

```powershell
# 1. Ingresar al directorio del backend
cd backend

# 2. Crear y activar el entorno virtual
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1

# 3. Instalar librerías requeridas
python -m pip install -r requirements.txt

# 4. Iniciar el servidor local
python -m app.run_local
```

El servidor quedará a la escucha en `http://127.0.0.1:8000` y la documentación interactiva de la API estará disponible en `http://127.0.0.1:8000/docs`.

### 4.2 Compilación del Frontend (React + Vite)

Para compilar manualmente la interfaz web:

```powershell
cd frontend
npm install
npm run build
```

Los archivos estáticos generados se ubican en `frontend/dist/` y son servidos directamente por FastAPI, garantizando que no se requiera un servidor Node.js en tiempo de ejecución.

---

## 5. Ejemplos Prácticos para Pruebas del Evaluador

Para evaluar el correcto funcionamiento de las diferentes familias implementadas en el motor matemático, se sugieren los siguientes ejercicios de prueba:

1. **Ecuación Lineal de Primer Orden con PVI:**
   - Ecuación: `y' + 3*y = 9`
   - Condiciones iniciales: $x_0 = 0$, $y_0 = 2$
   - *Resultado esperado:* Identifica el factor integrante $\mu(x) = e^{3x}$ y halla la solución particular $y(x) = 3 - e^{-3x}$.

2. **Ecuación Homogénea:**
   - Ecuación: `y' = (2*x + y) / x`
   - *Resultado esperado:* Detecta homogeneidad de grado 0, aplica el cambio de variable $y = u \cdot x$ y separa variables para obtener la solución.

3. **Ecuación Exacta (Modo Guiado):**
   - En el selector de tipo de ecuación, elija **Modo Guiado Exacta**.
   - Coeficiente $M(x, y)$: `4*x*y + 2`
   - Coeficiente $N(x, y)$: `2*x^2 + 6*y`
   - *Resultado esperado:* Verifica la condición de exactitud $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x} = 4x$ e integra la función potencial $\Psi(x, y) = 2x^2y + 2x + 3y^2 = C$.

4. **Ecuación de Segundo Orden Reducible:**
   - Ecuación: `y'' + y' = (y')^2`
   - Condiciones iniciales: $x_0 = 0$, $y_0 = 0$, $y'(x_0) = 1$
   - *Resultado esperado:* Realiza la sustitución $p = y'$, resuelve la ecuación de Bernoulli resultante para $p(x)$ y finalmente integra para obtener $y(x)$.

---

## 6. Verificación de Pruebas Unitarias

Para comprobar la validez matemática y la robustez del sistema frente a errores de sintaxis y casos de frontera, puede ejecutar la suite de pruebas unitarias con el siguiente comando:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -v
```

Todas las pruebas deben concluir en estado verde (`PASSED`), certificando que el parser seguro, el clasificador y los métodos de resolución cumplen con los estándares matemáticos exigidos.

---

## 7. Estructura y Arquitectura del Código

Para facilitar la revisión técnica por parte del Licenciado, se detalla la organización de los módulos principales:

- `backend/app/safe_math.py`: Analizador sintáctico seguro basado en el AST de Python. Limita estrictamente las funciones permitidas (`sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `Abs`) y previene cualquier inyección de código arbitrario.
- `backend/app/engine.py`: Motor simbólico que implementa la clasificación rigurosa, el cálculo analítico de soluciones y la verificación residual mediante sustitución en la ecuación diferencial original.
- `backend/app/main.py`: Punto de entrada de la API REST construida con FastAPI, encargada de comunicar el frontend con el motor matemático y de servir los archivos compilados de la interfaz.
- `backend/app/run_local.py`: Coordinador de ejecución local en Windows que gestiona la apertura automática del navegador y el bloqueo de instancias para evitar conflictos de puertos.
- `frontend/src/App.tsx`: Componente principal de la interfaz de usuario en React, integrando el editor interactivo MathLive, el renderizador KaTeX y el historial de consultas.
- `instalar.bat` e `iniciar.bat`: Automatizaciones en scripts por lotes diseñadas específicamente para un despliegue asistido y sin fricciones en sistemas Windows.

---

## 8. Solución de Problemas Frecuentes

- **Error: "No se encontró Python 3.10 o posterior"**:
  - Asegúrese de haber instalado Python marcando la opción *"Add python.exe to PATH"*. Si ya lo instaló sin marcarla, reinstale Python o añada la ruta a las Variables de Entorno del Sistema.
- **Error: "No se encontró Node.js"**:
  - Verifique que la instalación de Node.js haya finalizado y reinicie la terminal o el explorador para que Windows actualice las variables del sistema.
- **El navegador no se abre automáticamente**:
  - Si su navegador no se abre de forma automática al ejecutar `iniciar.bat`, abra manualmente cualquier navegador (Chrome, Edge, Firefox) e ingrese a `http://127.0.0.1:8000`.
- **Conflicto con el puerto 8000**:
  - Si otra aplicación en su computadora está utilizando el puerto 8000, cierre dicha aplicación antes de ejecutar `iniciar.bat`.
