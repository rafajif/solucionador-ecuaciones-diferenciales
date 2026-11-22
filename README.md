# 🧪 EDO Lab — Laboratorio Interactivo de Ecuaciones Diferenciales Ordinarias 🚀

<div align="center">

![EDO Lab Banner](https://img.shields.io/badge/EDO%20Lab-Matem%C3%A1tica%20IV-0876a6?style=for-the-badge&logo=math&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React_18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![SymPy](https://img.shields.io/badge/SymPy-Exact_Math-3B5526?style=for-the-badge&logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/Pytest-21%2F21%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)

</div>

---

### 📋 Ficha Técnica y Créditos Académicos

| 🏷️ Campo | 📌 Detalle |
| :--- | :--- |
| 🏛️ **Institución:** | **Universidad Dr. Andrés Bello (UNAB)** |
| 📚 **Asignatura:** | **Matemática IV** |
| 👨‍🏫 **Docente Evaluador:** | **Lic. Hernán Antonio Berríos Gámez** |
| 👨‍💻 **Desarrollador / Estudiante:** | **Rafael Atilio Umaña Majano** *(Carnet: `UM1240042023`)* |
| 💻 **Entorno de Ejecución:** | Windows 10 / 11 (100% Local y Seguro) |

---

## 🌟 1. Presentación del Proyecto

Estimado **Licenciado Hernán Antonio Berríos Gámez**:

Bienvenido a **EDO Lab**, un entorno interactivo y pedagógico desarrollado para la resolución analítica, clasificación automática y verificación residual exacta de **Ecuaciones Diferenciales Ordinarias (EDO)**.

La herramienta combina un **núcleo de cálculo simbólico en Python (FastAPI + SymPy)** con una **interfaz gráfica moderna y responsiva en React**, equipada con editor matemático en vivo mediante **MathLive** y renderizado algebraico en **KaTeX**.

> [!NOTE]
> 🔒 **100% Local y Autónomo:** EDO Lab no requiere conexión a internet para su uso diario, no envía datos a servidores externos ni utiliza modelos generativos probabilísticos; cada paso es calculado y verificado algebraicamente por el motor simbólico.

---

## 🎯 2. Familias de EDO Soportadas

El sistema clasifica e implementa los métodos analíticos correspondientes a los contenidos de la **Guía de Estudio de Matemática IV (UNAB)**:

1. 📈 **Lineales de 1.er Orden:** $y' + P(x)y = Q(x)$ mediante factor integrante $\mu(x) = e^{\int P(x)\,dx}$.
2. 🔄 **Homogéneas:** $y' = F(x, y)$ con sustitución $y = v \cdot x$.
3. 🎯 **Exactas:** $M(x, y)\,dx + N(x, y)\,dy = 0$ con prueba de Euler $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x}$ y cálculo de la función potencial $\Psi(x, y) = C$ (disponible también en **Modo Guiado**).
4. ⚡ **Variables Separables:** $g(y)\,dy = f(x)\,dx$ con integración en cuadratura directa.
5. 🌊 **Ecuaciones de Bernoulli:** $y' + P(x)y = Q(x)y^n$ mediante transformación $u = y^{1-n}$.
6. 🔬 **2.º Orden Reducibles (Bernoulli Autónomo):** Familias de la forma $p' = A\,p + B\,p^n$ con la reducción $p = y'$.

---

## ⚙️ 3. Requisitos Previos del Sistema

Antes de iniciar la instalación en Windows, asegúrese de contar con:

* 🐍 **Python 3.10 o superior** (Recomendado 3.11 o 3.12):  
  📥 Descargar: [python.org/downloads/windows](https://www.python.org/downloads/windows/)  
  > [!IMPORTANT]
  > Durante la instalación de Python, es fundamental marcar la casilla:  
  > **☑ "Add python.exe to PATH"** (o *"Agregar Python al PATH"*).

* 🟩 **Node.js 20 LTS o superior** (incluye `npm`):  
  📥 Descargar: [nodejs.org](https://nodejs.org/)

> [!TIP]
> 🌐 **Sobre el uso de Internet:** Solo se necesita conexión la primera vez para descargar las dependencias. Una vez compilado, EDO Lab funciona de forma **completamente offline**.

---

## 🚀 4. Guía Rápida de Instalación y Uso (¡Método Sencillo con 1 Clic!)

Se han creado dos scripts automatizados (`.bat`) para que la puesta en marcha sea inmediata:

```
📁 Proyecto EDO Lab
 ├── ⚙️ instalar.bat   <-- [Paso 1: Ejecutar una sola vez]
 ├── 🚀 iniciar.bat    <-- [Paso 2: Para abrir la aplicación siempre]
 ├── 📂 backend/       <-- Motor simbólico FastAPI + SymPy
 └── 📂 frontend/      <-- Interfaz visual React + MathLive
```

### 📦 Paso 1: Instalación Inicial Automática

1. Diríjase a la carpeta raíz del proyecto.
2. Haga **doble clic** en el archivo [instalar.bat](file:///c:/Users/Dell_E7270/Desktop/Programa/instalar.bat).
3. El instalador ejecutará de forma asistida:
   - 🔹 **[1/6]** Creación del entorno virtual aislado de Python (`.venv`).
   - 🔹 **[2/6]** Instalación de librerías del backend (`FastAPI`, `SymPy`, `Uvicorn`, etc.).
   - 🔹 **[3/6]** Descarga de paquetes del frontend (`npm install`).
   - 🔹 **[4/6]** Compilación de la aplicación web a producción (`frontend/dist`).
   - 🔹 **[5/6]** Ejecución de la batería de pruebas automáticas (`pytest` — 21/21).
   - 🔹 **[6/6]** Verificación de integridad del sistema.
4. Al terminar con éxito, verá en pantalla:
   ```text
   ================================================
   Instalacion completada correctamente.
   Ahora ejecuta iniciar.bat para abrir EDO Lab.
   ================================================
   ```

---

### ▶️ Paso 2: Iniciar la Aplicación

1. Haga **doble clic** en el archivo [iniciar.bat](file:///c:/Users/Dell_E7270/Desktop/Programa/iniciar.bat).
2. Se iniciará el servidor local y **automáticamente se abrirá su navegador web** en:
   $$\text{http://127.0.0.1:8000}$$
3. ¡Listo! Ya puede ingresar ecuaciones, cargar ejemplos y explorar los pasos analíticos.

> [!TIP]
> 🛑 **Para cerrar el sistema:**  
> Mantenga abierta la consola de comandos mientras use la app. Para salir, presione `Ctrl + C` en la ventana negra o simplemente ciérrela.

---

## 🛠️ 5. Ejecución Manual Alternativa (PowerShell / CMD)

Si el Licenciado desea ejecutar los servicios por separado o inspeccionar el código:

### 🐍 Backend (FastAPI + SymPy)
```powershell
# 1. Entrar al directorio backend y activar entorno
cd backend
..\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
python -m pip install -r requirements.txt

# 3. Iniciar el servidor local
python -m app.run_local
```
*API local:* `http://127.0.0.1:8000` | *Documentación Swagger:* `http://127.0.0.1:8000/docs`

### ⚛️ Frontend (React + Vite)
```powershell
cd frontend
npm install
npm run build    # Compila a frontend/dist para ser servido por FastAPI
# o bien para desarrollo en vivo:
npm run dev
```

---

## 📚 6. Ejemplos Prácticos de Evaluación (Guía Matemática IV UNAB)

Dentro de la aplicación encontrará un **Panel de Ejemplos Rápidos** organizado por categorías, alineado directamente con la guía de estudio:

| Categoría | Ecuación de Ejemplo | Condiciones | Resultado Clave |
| :--- | :--- | :--- | :--- |
| 📈 **Lineal (Ej. 1)** | `y' + 3*y = 9` | $x_0 = 0,\; y_0 = 2$ | Factor integrante $\mu = e^{3x} \implies y(x) = 3 - e^{-3x}$ |
| 📈 **Lineal (Ej. 2)** | `y' + 0.4*y = 8` | $x_0 = 0,\; y_0 = 5$ | Admite coeficientes decimales y simplificación racional |
| 🎯 **Exacta (Ej. 3)** | `(4*x*y + 2)*dx + (2*x^2 + 6*y)*dy = 0` | — | $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x} = 4x \implies \Psi(x,y) = 2x^2y + 2x + 3y^2 = C$ |
| 🎯 **Exacta (Ej. 4)** | `(2*x + y)*dx + (x + 4*y)*dy = 0` | — | Exactitud demostrada y función potencial calculada paso a paso |
| 🔄 **Homogénea (Ej. 5)** | `y' = (2*x + y) / x` | — | Sustitución $y = vx \implies v'x + v = 2 + v \implies v(x) = \ln\|Cx^2\|$ |
| ⚡ **Separable** | `y' = x * y` | $x_0 = 0,\; y_0 = 1$ | $\frac{dy}{y} = x\,dx \implies y(x) = e^{x^2/2}$ |
| 🌊 **Bernoulli** | `y' + y = x * y^2` | — | Reducción con $u = y^{-1}$ a ecuación lineal |
| 🔬 **2.º Orden Reducible** | `y'' + y' = (y')^2` | $x_0 = 0,\; y_0 = 0,\; y'(0) = 1$ | Cambio $p = y'$ con solución de equilibrios y ramas |

---

## 🧪 7. Pruebas Unitarias Automatizadas

El proyecto incluye una suite completa de pruebas unitarias que validan el analizador seguro (`safe_math`), el clasificador y los resolvedores:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -v
```

> [!NOTE]
> ✅ **Resultado:** 21 pruebas unitarias pasando satisfactoriamente (`21 passed`), garantizando la exactitud matemática y la estabilidad de la plataforma.

---

## 🏛️ 8. Arquitectura y Seguridad del Código

* 🛡️ **`backend/app/safe_math.py`:** Parser algebraico seguro basado en el árbol sintáctico (AST) de Python. Previene cualquier ejecución de código malicioso o arbitrario y restringe las funciones a un conjunto matemático seguro (`sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `Abs`).
* 🧠 **`backend/app/engine.py`:** Motor matemático que ejecuta la clasificación por orden de precedencia, resuelve simbólicamente con SymPy y verifica la solución sustituyendo en la ecuación diferencial original para comprobar que el residuo sea nulo.
* ⚡ **`backend/app/main.py`:** API REST construida con FastAPI que expone los endpoints `/api/identificar`, `/api/resolver` y sirve la aplicación compilada del frontend sin necesidad de procesos Node en producción.
* 🖥️ **`backend/app/run_local.py`:** Gestor de ejecución local en Windows con bloqueo por instancia para evitar puertos duplicados y apertura automatizada del navegador.
* 🎨 **`frontend/src/App.tsx`:** Interfaz web interactiva con panel de ejemplos, barra de inserción rápida de operadores, historial local y renderizado en LaTeX.

---

## 💡 9. Preguntas Frecuentes y Solución de Problemas

* ❓ **¿Qué hacer si `instalar.bat` indica que no encuentra Python?**  
  👉 Reinstale Python asegurándose de marcar la casilla **"Add python.exe to PATH"**.
* ❓ **¿Qué hacer si `instalar.bat` indica que falta Node.js?**  
  👉 Descargue e instale Node.js 20 LTS desde [nodejs.org](https://nodejs.org/).
* ❓ **¿El navegador no se abrió automáticamente con `iniciar.bat`?**  
  👉 Abra manualmente su navegador favorito (Edge, Chrome, Firefox) e ingrese a `http://127.0.0.1:8000`.
* ❓ **¿Conflicto con el puerto 8000?**  
  👉 Verifique que no haya otra instancia de EDO Lab o de otra aplicación corriendo en el puerto 8000.

---

<div align="center">

**EDO Lab** — Desarrollado para la Cátedra de **Matemática IV**  
*Universidad Dr. Andrés Bello (UNAB)*  
El Salvador 🇸🇻

</div>
