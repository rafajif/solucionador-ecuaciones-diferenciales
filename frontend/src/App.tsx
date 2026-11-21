import { useRef, useState } from 'react'
import katex from 'katex'
import {
  Activity, ArrowRight, BookOpen, Check, ChevronDown, ChevronRight,
  CircleHelp, Copy, Moon, RotateCcw, Sparkles, Sun, Zap, AlertCircle, Info
} from 'lucide-react'
import type { MathfieldElement } from 'mathlive'

type Step = {
  numero: number
  titulo: string
  explicacion: string
  expresion_latex: string
  operacion: string
  justificacion: string
}
type Answer = {
  tipo_ecuacion: string
  metodo: string
  solucion_latex: string
  tipo_solucion: string
  orden: number
  pasos: Step[]
  verificacion: { estado: string; residuo?: string }
  restricciones_dominio?: string[]
}

function Formula({ latex, display = false }: { latex: string; display?: boolean }) {
  try {
    return (
      <span
        className={display ? 'formula display' : 'formula'}
        dangerouslySetInnerHTML={{
          __html: katex.renderToString(latex, {
            throwOnError: false,
            displayMode: display,
            strict: 'ignore',
          }),
        }}
      />
    )
  } catch {
    return <code>{latex}</code>
  }
}

const TYPE_LABELS: Record<string, string> = {
  lineal_primer_orden: 'Lineal de 1er orden',
  exacta: 'Exacta',
  homogenea_primer_orden: 'Homogénea de 1er orden',
  segundo_orden_reducible_bernoulli: '2do orden (Bernoulli)',
  separable: 'Separable',
  bernoulli: 'Bernoulli',
}
const METHOD_LABELS: Record<string, string> = {
  factor_integrante: 'Factor integrante',
  funcion_potencial: 'Función potencial',
  sustitucion_y_vx: 'Sustitución y = vx',
  sustitucion_p_yprime: 'Sustitución p = y′',
  separacion_variables: 'Separación de variables',
  sustitucion_bernoulli: 'Sustitución de Bernoulli',
}

// Ejemplos por categoría — alineados con la Guía de Estudio Matemática IV (UNAB)
const EXAMPLES = [
  {
    label: 'Lineal',
    color: '#0876a6',
    bg: '#e8f6fc',
    items: [
      { title: "y' + 3y = 9", eq: "y'+3*y=9", x0: '0', y0: '2', desc: 'Guía Ej. 1' },
      { title: "y' + 0.4y = 8", eq: "y'+0.4*y=8", x0: '0', y0: '5', desc: 'Guía Ej. 2' },
      { title: "y' + 2y = 6", eq: "y'+2*y=6", x0: '0', y0: '1', desc: 'Factor integrante' },
      { title: "y' - y = eˣ", eq: "y'-y=exp(x)", desc: 'Solución general' },
    ],
  },
  {
    label: 'Exacta',
    color: '#92400e',
    bg: '#fffbeb',
    items: [
      { title: '(4xy+2)dx+(2x²+6y)dy=0', eq: '(4*x*y+2)*dx+(2*x^2+6*y)*dy=0', desc: 'Guía Ej. 3' },
      { title: '(2x+y)dx+(x+4y)dy=0', eq: '(2*x+y)*dx+(x+4*y)*dy=0', desc: 'Guía Ej. 4' },
      { title: 'M=2xy+3x², N=x²+4y', M: '2*x*y+3*x^2', N: 'x^2+4*y', isExact: true, desc: 'Modo guiado' },
      { title: 'M=4xy+2, N=2x²+6y', M: '4*x*y+2', N: '2*x^2+6*y', isExact: true, desc: 'Modo guiado' },
    ],
  },
  {
    label: 'Homogénea',
    color: '#065f46',
    bg: '#ecfdf5',
    items: [
      { title: "y' = (2x+y)/x", eq: "y'=(2*x+y)/x", desc: 'Guía Ej. 5' },
      { title: "y' = (x+y)/x", eq: "y'=(x+y)/x", desc: 'Guía ejemplo' },
      { title: "y' = y/x + 1", eq: "y'=y/x+1", desc: 'Forma equivalente' },
    ],
  },
  {
    label: 'Separable',
    color: '#7c3aed',
    bg: '#f3f0ff',
    items: [
      { title: "y' = xy", eq: "y'=x*y", desc: 'Separable simple' },
      { title: "y' = x/y", eq: "y'=x/y", desc: 'Variables separadas' },
      { title: "y' = y²·x", eq: "y'=x*y^2", x0: '0', y0: '1', desc: 'Con CI' },
    ],
  },
  {
    label: 'Bernoulli',
    color: '#be185d',
    bg: '#fdf2f8',
    items: [
      { title: "y' = y - y²", eq: "y'=y-y^2", desc: 'Logística n=2' },
      { title: "y' = 2y - xy²", eq: "y'=2*y-x*y^2", desc: 'Coef. variable' },
      { title: "y' = y + y³", eq: "y'=y+y^3", desc: 'n=3' },
    ],
  },
  {
    label: '2do orden',
    color: '#1d4ed8',
    bg: '#eff6ff',
    items: [
      { title: "y''+y'=(y')²", eq: "y''+y'=(y')^2", x0: '0', y0: '0', yp0: '1', desc: 'Guía Ej. 6' },
      { title: "y''+2y'=2(y')³", eq: "y''+2*y'=2*(y')^3", x0: '0', y0: '2', yp0: '1', desc: 'Guía Ej. 7' },
      { title: "y''+3y'=3(y')²", eq: "y''+3*y'=3*(y')^2", x0: '0', y0: '0', yp0: '1', desc: 'Guía Ej. 8' },
      { title: "y''+y'=2(y')³", eq: "y''+y'=2*(y')^3", x0: '0', y0: '0', yp0: '1', desc: 'Guía Ej. 9' },
      { title: "y''+2y'=4(y')²", eq: "y''+2*y'=4*(y')^2", x0: '0', y0: '0', yp0: '1', desc: 'Guía Ej. 10' },
    ],
  },
]

type ExampleItem = {
  title: string
  eq?: string
  M?: string
  N?: string
  isExact?: boolean
  x0?: string
  y0?: string
  yp0?: string
  desc?: string
}

export default function App() {
  const field = useRef<MathfieldElement | null>(null)
  const [equation, setEquation] = useState("y'+3*y=9")
  const [mode, setMode] = useState('automatico')
  const [guided, setGuided] = useState('lineal')
  const [M, setM] = useState('4*x*y+2')
  const [N, setN] = useState('2*x^2+6*y')
  const [x0, setX0] = useState('')
  const [y0, setY0] = useState('')
  const [yp0, setYp0] = useState('')
  const [answer, setAnswer] = useState<Answer | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [openSteps, setOpenSteps] = useState(true)
  const [dark, setDark] = useState(false)
  const [history, setHistory] = useState<string[]>(() =>
    JSON.parse(localStorage.getItem('edo-history') || '[]')
  )
  const [activeExGroup, setActiveExGroup] = useState<number | null>(null)
  const [copied, setCopied] = useState(false)

  const isSecondOrder = (value: string) =>
    /y\s*''|y\s*\^\s*\{\s*\\prime\\prime\s*\}/.test(value)

  const insert = (latex: string) => {
    const mf = field.current
    if (!mf) return
    mf.insert(latex)
    mf.focus()
  }

  const loadExample = (item: ExampleItem) => {
    setAnswer(null); setError(''); setNotice('')
    if (item.isExact) {
      setMode('guiado'); setGuided('exacta')
      setM(item.M ?? ''); setN(item.N ?? '')
    } else {
      const eq = item.eq ?? ''
      setEquation(eq)
      if (field.current) field.current.value = eq
      setMode('automatico')
    }
    setX0(item.x0 ?? ''); setY0(item.y0 ?? ''); setYp0(item.yp0 ?? '')
    setActiveExGroup(null)
  }

  const solve = async (identify = false) => {
    const eq = field.current?.getValue('latex') ?? equation
    const hasX0 = x0.trim().length > 0
    const hasY0 = y0.trim().length > 0
    const hasYp0 = yp0.trim().length > 0
    const guidedExact = mode === 'guiado' && guided === 'exacta'
    if (!identify && !guidedExact) {
      if (hasX0 !== hasY0) {
        setError('Completa ambos datos de la condición inicial: x₀ e y(x₀).')
        setNotice(''); return
      }
      if (isSecondOrder(eq) && !(hasX0 && hasY0 && hasYp0)) {
        setError('Para resolver esta ecuación de segundo orden, completa x₀, y(x₀) e y′(x₀).')
        setNotice(''); return
      }
    }
    setEquation(eq); setBusy(true); setError(''); setNotice('')
    try {
      const guidedMode =
        mode === 'guiado'
          ? guided === 'bernoulli' ? 'bernoulli'
          : guided === 'separable' ? 'separable'
          : guided === 'exacta' ? 'exacta'
          : guided === 'homogenea' ? 'homogenea'
          : 'lineal'
          : 'automatico'
      const body: Record<string, string> =
        guidedExact
          ? { modo: 'exacta', M, N }
          : {
              ecuacion: eq,
              modo: mode === 'guiado' ? guidedMode : 'automatico',
              ...(x0.trim() && y0.trim() ? { x0, y0 } : {}),
              ...(isSecondOrder(eq) && x0.trim() && y0.trim() && yp0.trim() ? { yp0 } : {}),
            }
      const response = await fetch(`/api/${identify ? 'identificar' : 'resolver'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'No se pudo procesar la ecuación.')
      if (identify) {
        setAnswer({
          tipo_ecuacion: data.familias_compatibles?.[0] || 'Sin clasificar',
          metodo: data.metodo_prioritario || 'No determinado',
          orden: data.orden,
          pasos: [],
          solucion_latex: '',
          tipo_solucion: '',
          verificacion: { estado: 'indeterminada' },
        })
        return
      }
      setAnswer(data)
      if (!guidedExact && data.tipo_solucion === 'general') {
        setNotice(
          'Se obtuvo la solución general. Puedes añadir condiciones iniciales para obtener una solución particular.'
        )
      }
      const next = [eq, ...history.filter(v => v !== eq)].slice(0, 12)
      setHistory(next)
      localStorage.setItem('edo-history', JSON.stringify(next))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al conectar con el backend local.')
    } finally {
      setBusy(false)
    }
  }

  const clear = () => {
    setEquation('')
    if (field.current) field.current.value = ''
    setAnswer(null); setError(''); setNotice('')
    setX0(''); setY0(''); setYp0('')
  }

  const copy = async () => {
    if (!answer) return
    await navigator.clipboard.writeText(answer.solucion_latex)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const guidedExact = mode === 'guiado' && guided === 'exacta'

  return (
    <main className={dark ? 'app dark' : 'app'}>
      {/* ── Top bar ── */}
      <header className="topbar">
        <a className="brand" href="#">
          <span className="brandmark"><Activity size={20} /></span>
          <span>EDO <b>LAB</b></span>
        </a>
        <div className="toplinks">
          <span className="offline"><i /> Motor local</span>
          <button className="icon-button" aria-label="Cambiar tema" onClick={() => setDark(!dark)}>
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <span className="avatar">M</span>
        </div>
      </header>

      <div className="layout">
        {/* ── Sidebar ── */}
        <aside className="sidebar">
          <div className="side-label">ESPACIO DE TRABAJO</div>
          <button className="nav-item active"><Activity size={17} /> Resolver EDO</button>
          <button
            className="nav-item"
            onClick={() => document.getElementById('history')?.scrollIntoView({ behavior: 'smooth' })}
          >
            <RotateCcw size={17} /> Historial local
          </button>
          <div className="side-label types-label">TIPOS IMPLEMENTADOS</div>
          {[
            ['01', 'Lineal 1er orden'],
            ['02', 'Separable'],
            ['03', 'Homogénea'],
            ['04', 'Exacta'],
            ['05', 'Bernoulli'],
            ['06', '2do orden (p=y′)'],
          ].map(([num, label]) => (
            <div className="method-item" key={num}>
              <span className="method-num">{num}</span>{label}
            </div>
          ))}
          <div className="sidebar-note">
            <BookOpen size={17} />
            <div>
              <b>Procedimientos paso a paso</b>
              <p>Cada resolución muestra la justificación matemática completa.</p>
            </div>
          </div>
        </aside>

        {/* ── Main content ── */}
        <section className="content">
          <div className="heading">
            <div>
              <div className="eyebrow"><Sparkles size={14} /> LABORATORIO DE MATEMÁTICAS</div>
              <h1>Resuelve una EDO</h1>
              <p>Identifica el tipo, aplica el método y verifica la solución simbólicamente.</p>
            </div>
            <button className="help-button"><CircleHelp size={16} /> Guía rápida</button>
          </div>

          {/* ── Examples panel ── */}
          <div className="examples-panel">
            <div className="examples-header">
              <Zap size={13} />
              <span>EJEMPLOS RÁPIDOS</span>
              <span className="examples-hint">Haz clic en un tipo para ver los ejemplos</span>
            </div>
            <div className="examples-groups">
              {EXAMPLES.map((group, gi) => (
                <div key={gi} className="ex-group">
                  <button
                    className={`ex-group-btn${activeExGroup === gi ? ' active' : ''}`}
                    style={activeExGroup === gi ? { background: group.bg, color: group.color, borderColor: group.color } : {}}
                    onClick={() => setActiveExGroup(activeExGroup === gi ? null : gi)}
                  >
                    {group.label}
                  </button>
                  {activeExGroup === gi && (
                    <div className="ex-dropdown">
                      {group.items.map((item, ii) => (
                        <button
                          key={ii}
                          className="ex-item"
                          onClick={() => loadExample(item)}
                        >
                          <code className="ex-eq">{item.title}</code>
                          {item.desc && <span className="ex-desc">{item.desc}</span>}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* ── Workspace ── */}
          <div className="workspace">
            <div className="workspace-head">
              <div>
                <span className="section-index">01</span>
                <b>Planteamiento</b>
              </div>
              <div className="segmented">
                <button
                  className={mode === 'automatico' ? 'selected' : ''}
                  onClick={() => setMode('automatico')}
                >
                  Automático
                </button>
                <button
                  className={mode === 'guiado' ? 'selected' : ''}
                  onClick={() => setMode('guiado')}
                >
                  Modo guiado
                </button>
              </div>
            </div>

            {mode === 'guiado' && (
              <div className="guided-row">
                <label>
                  Familia
                  <select value={guided} onChange={e => setGuided(e.target.value)}>
                    <option value="lineal">Lineal de primer orden</option>
                    <option value="separable">Separable</option>
                    <option value="exacta">Exacta</option>
                    <option value="homogenea">Homogénea de primer orden</option>
                    <option value="bernoulli">Bernoulli</option>
                    <option value="bernoulli2">2do orden reducible a Bernoulli</option>
                  </select>
                </label>
              </div>
            )}

            {/* Equation editor or exact fields */}
            {!guidedExact ? (
              <>
                <div className="editor-label">ECUACIÓN DIFERENCIAL</div>
                <math-field
                  ref={el => { field.current = el as MathfieldElement | null }}
                  className="math-editor"
                  onInput={event => setEquation((event.target as MathfieldElement).getValue('latex'))}
                  value={equation}
                  virtual-keyboard-mode="manual"
                >
                  {equation}
                </math-field>

                {/* Symbol bar — grouped */}
                <div className="symbolbar">
                  <span className="sym-sep">Variables</span>
                  {[
                    ['x', 'x'],
                    ['y', 'y'],
                    ['dx', 'dx'],
                    ['dy', 'dy'],
                  ].map(([title, token]) => (
                    <button
                      key={title}
                      type="button"
                      onMouseDown={e => e.preventDefault()}
                      onClick={() => insert(token)}
                      title={`Insertar ${title}`}
                    >
                      {title}
                    </button>
                  ))}
                  <span className="sym-sep">Derivadas</span>
                  {[
                    ["y'", "y'"],
                    ["y''", "y''"],
                  ].map(([title, token]) => (
                    <button
                      key={title}
                      type="button"
                      onMouseDown={e => e.preventDefault()}
                      onClick={() => insert(token)}
                      title={`Insertar ${title}`}
                    >
                      {title}
                    </button>
                  ))}
                  <span className="sym-sep">Operaciones</span>
                  {[
                    ['a/b', '\\frac{#@}{#?}'],
                    ['xⁿ', '^{}'],
                    ['√', '\\sqrt{}'],
                    ['|x|', '\\left|#@\\right|'],
                    ['( )', '()'],
                  ].map(([title, token]) => (
                    <button
                      key={title}
                      type="button"
                      onMouseDown={e => e.preventDefault()}
                      onClick={() => insert(token)}
                      title={`Insertar ${title}`}
                    >
                      {title}
                    </button>
                  ))}
                  <span className="sym-sep">Funciones</span>
                  {[
                    ['eˣ', 'e^{x}'],
                    ['ln', '\\ln'],
                    ['sin', '\\sin'],
                    ['cos', '\\cos'],
                    ['tan', '\\tan'],
                    ['√x', '\\sqrt{x}'],
                  ].map(([title, token]) => (
                    <button
                      key={title}
                      type="button"
                      onMouseDown={e => e.preventDefault()}
                      onClick={() => insert(token)}
                      title={`Insertar ${title}`}
                    >
                      {title}
                    </button>
                  ))}
                  <span className="sym-sep">Constantes</span>
                  {[
                    ['π', '\\pi'],
                    ['e', 'e'],
                  ].map(([title, token]) => (
                    <button
                      key={title}
                      type="button"
                      onMouseDown={e => e.preventDefault()}
                      onClick={() => insert(token)}
                      title={`Insertar ${title}`}
                    >
                      {title}
                    </button>
                  ))}
                </div>

                <div className="editor-hint">
                  <Info size={11} />
                  Escribe directamente o usa los botones. Ejemplos: <code>y'+3*y=9</code> · <code>y'=x*y</code> · <code>(x+y)*dx+(x+2*y)*dy=0</code>
                </div>
              </>
            ) : (
              <div className="exact-fields">
                <label>
                  M(x,y)
                  <input value={M} onChange={e => setM(e.target.value)} placeholder="ej: 4*x*y+2" />
                </label>
                <label>
                  N(x,y)
                  <input value={N} onChange={e => setN(e.target.value)} placeholder="ej: 2*x^2+6*y" />
                </label>
                <div className="exact-hint">Ecuación en forma M dx + N dy = 0</div>
              </div>
            )}

            {/* Initial conditions */}
            <div className="conditions">
              <div className="condition-title">
                CONDICIONES INICIALES <span>OPCIONAL</span>
              </div>
              <div className="condition-fields">
                <label>
                  x₀
                  <input value={x0} onChange={e => setX0(e.target.value)} placeholder="ej: 0" />
                </label>
                <label>
                  y(x₀)
                  <input value={y0} onChange={e => setY0(e.target.value)} placeholder="ej: 1" />
                </label>
                {isSecondOrder(equation) && (
                  <label>
                    y′(x₀)
                    <input value={yp0} onChange={e => setYp0(e.target.value)} placeholder="ej: 1" />
                  </label>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="actions">
              <button className="primary" disabled={busy} onClick={() => solve(false)}>
                {busy ? 'Resolviendo…' : 'Resolver ecuación'}
                <ArrowRight size={17} />
              </button>
              <button className="secondary" disabled={busy} onClick={() => solve(true)}>
                Identificar tipo
              </button>
              <button className="clear" onClick={clear}>Limpiar</button>
            </div>
          </div>

          {/* Error / notice */}
          {error && (
            <div className="error">
              <AlertCircle size={14} />
              {error}
            </div>
          )}
          {notice && (
            <div className="notice" role="status">
              <Info size={14} />
              {notice}
            </div>
          )}

          {/* Result card */}
          {answer && (
            <section className="result-card">
              <div className="result-header">
                <div>
                  <div className="result-kicker"><Check size={14} /> ANÁLISIS COMPLETADO</div>
                  <h2>Resultado</h2>
                </div>
                {answer.solucion_latex && (
                  <button className="copy-button" onClick={copy}>
                    <Copy size={15} /> {copied ? '¡Copiado!' : 'Copiar LaTeX'}
                  </button>
                )}
              </div>

              {/* Metadata chips */}
              <div className="metadata">
                <div>
                  <small>TIPO DE ECUACIÓN</small>
                  <b>{TYPE_LABELS[answer.tipo_ecuacion] || answer.tipo_ecuacion}</b>
                </div>
                <div>
                  <small>MÉTODO</small>
                  <b>{METHOD_LABELS[answer.metodo] || answer.metodo}</b>
                </div>
                <div>
                  <small>ORDEN</small>
                  <b>{answer.orden}°</b>
                </div>
              </div>

              {/* Solution display */}
              {answer.solucion_latex && (
                <div className="solution">
                  <span className="solution-caption">
                    {answer.tipo_solucion === 'particular'
                      ? 'SOLUCIÓN PARTICULAR'
                      : answer.tipo_solucion === 'implícita'
                      ? 'SOLUCIÓN IMPLÍCITA'
                      : 'SOLUCIÓN GENERAL'}
                  </span>
                  <Formula latex={answer.solucion_latex} display />
                  <div
                    className={`verify ${
                      answer.verificacion.estado === 'correcta'
                        ? 'good'
                        : answer.verificacion.estado === 'fallida'
                        ? 'bad'
                        : 'neutral'
                    }`}
                  >
                    <span>
                      {answer.verificacion.estado === 'correcta'
                        ? '✓'
                        : answer.verificacion.estado === 'fallida'
                        ? '✗'
                        : '·'}
                    </span>
                    Verificación simbólica:{' '}
                    <strong>{answer.verificacion.estado}</strong>
                    {answer.verificacion.residuo && answer.verificacion.residuo !== '0' && (
                      <span className="residuo">
                        {' '}— residuo: <Formula latex={answer.verificacion.residuo} />
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Steps */}
              {answer.pasos.length > 0 && (
                <>
                  <button
                    className="steps-toggle"
                    onClick={() => setOpenSteps(!openSteps)}
                  >
                    <span>
                      <span className="section-index">02</span>
                      <b>Procedimiento paso a paso</b>
                      <em>{answer.pasos.length} pasos</em>
                    </span>
                    {openSteps ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  </button>
                  {openSteps && (
                    <div className="steps">
                      {answer.pasos.map(s => (
                        <article className="step" key={s.numero}>
                          <div className="step-number">{String(s.numero).padStart(2, '0')}</div>
                          <div className="step-body">
                            <h3>{s.titulo}</h3>
                            <p>{s.explicacion}</p>
                            <div className="step-math">
                              <Formula latex={s.expresion_latex} display />
                            </div>
                            <div className="reason">
                              <b>Justificación</b>
                              {s.justificacion}
                            </div>
                          </div>
                        </article>
                      ))}
                    </div>
                  )}
                </>
              )}

              {answer.restricciones_dominio?.length ? (
                <div className="domain">
                  <b>Dominio y ramas:</b> {answer.restricciones_dominio.join(' · ')}
                </div>
              ) : null}
            </section>
          )}

          {/* History */}
          <section id="history" className="history">
            <div>
              <h2>Últimas ecuaciones</h2>
              <p>Guardadas en este dispositivo.</p>
            </div>
            {history.length ? (
              <div className="history-items">
                {history.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setEquation(item)
                      if (field.current) field.current.value = item
                    }}
                  >
                    {item}
                  </button>
                ))}
              </div>
            ) : (
              <span className="empty-history">Aún no hay ecuaciones resueltas.</span>
            )}
          </section>

          <footer>
            <span>EDO LAB <i>·</i> Herramienta educativa local</span>
            <span>Sin servicios externos</span>
          </footer>
        </section>
      </div>
    </main>
  )
}
