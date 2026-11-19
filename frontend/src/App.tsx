import { useRef, useState } from 'react'
import katex from 'katex'
import { Activity, ArrowRight, BookOpen, Check, ChevronDown, ChevronRight, CircleHelp, Copy, Moon, RotateCcw, Sparkles, Sun } from 'lucide-react'

type MathField = HTMLElement & { value: string; executeCommand: (command: string, args?: unknown[]) => void }
type Step = { numero: number; titulo: string; explicacion: string; expresion_latex: string; operacion: string; justificacion: string }
type Answer = { tipo_ecuacion: string; metodo: string; solucion_latex: string; tipo_solucion: string; orden: number; pasos: Step[]; verificacion: { estado: string; residuo?: string }; restricciones_dominio?: string[] }

function Formula({ latex, display = false }: { latex: string; display?: boolean }) {
  try { return <span className={display ? 'formula display' : 'formula'} dangerouslySetInnerHTML={{ __html: katex.renderToString(latex, { throwOnError: false, displayMode: display, strict: 'ignore' }) }} /> }
  catch { return <code>{latex}</code> }
}

const labels: Record<string, string> = { lineal_primer_orden: 'Lineal de primer orden', exacta: 'Exacta', homogenea_primer_orden: 'Homogénea de primer orden', segundo_orden_reducible_bernoulli: 'Segundo orden reducible a Bernoulli', factor_integrante: 'Factor integrante', funcion_potencial: 'Función potencial', sustitucion_y_vx: 'Sustitución y = vx', sustitucion_p_yprime: 'Sustitución p = y′' }

export default function App() {
  const field = useRef<MathField>(null)
  const [equation, setEquation] = useState("y'+3*y=9")
  const [mode, setMode] = useState('automatico')
  const [guided, setGuided] = useState('lineal')
  const [M, setM] = useState('4*x*y+2'); const [N, setN] = useState('2*x^2+6*y')
  const [x0, setX0] = useState(''); const [y0, setY0] = useState(''); const [yp0, setYp0] = useState('')
  const [answer, setAnswer] = useState<Answer | null>(null)
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false)
  const [openSteps, setOpenSteps] = useState(true); const [dark, setDark] = useState(false)
  const [history, setHistory] = useState<string[]>(() => JSON.parse(localStorage.getItem('edo-history') || '[]'))

  const insert = (latex: string) => field.current?.executeCommand('insert', [latex])
  const solve = async (identify = false) => {
    const eq = field.current?.value || equation
    setEquation(eq); setBusy(true); setError('')
    try {
      const body: Record<string, string> = mode === 'guiado' && guided === 'exacta'
        ? { modo: 'exacta', M, N }
        : { ecuacion: eq, modo: mode === 'guiado' ? (guided === 'bernoulli' ? 'automatico' : guided) : 'automatico', ...(x0.trim() && y0.trim() ? { x0, y0 } : {}), ...(eq.includes("y''") && x0.trim() && y0.trim() && yp0.trim() ? { yp0 } : {}) }
      const response = await fetch(`http://127.0.0.1:8000/api/${identify ? 'identificar' : 'resolver'}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'No se pudo procesar la ecuación.')
      if (identify) { setAnswer({ tipo_ecuacion: data.familias_compatibles?.[0] || 'Sin clasificar', metodo: data.metodo_prioritario || 'No determinado', orden: data.orden, pasos: [], solucion_latex: '', tipo_solucion: '', verificacion: { estado: 'indeterminada' } }); return }
      setAnswer(data)
      const next = [eq, ...history.filter(v => v !== eq)].slice(0, 12); setHistory(next); localStorage.setItem('edo-history', JSON.stringify(next))
    } catch (e) { setError(e instanceof Error ? e.message : 'Error al conectar con el backend local.') }
    finally { setBusy(false) }
  }
  const clear = () => { setEquation(''); if (field.current) field.current.value = ''; setAnswer(null); setError('') }
  const copy = async () => { if (!answer) return; await navigator.clipboard.writeText(answer.solucion_latex); }

  return <main className={dark ? 'app dark' : 'app'}>
    <header className="topbar"><a className="brand" href="#"><span className="brandmark"><Activity size={20}/></span><span>EDO <b>LAB</b></span></a><div className="toplinks"><span className="offline"><i/> Motor local</span><button className="icon-button" aria-label="Cambiar tema" onClick={() => setDark(!dark)}>{dark ? <Sun size={18}/> : <Moon size={18}/>}</button><span className="avatar">M</span></div></header>
    <div className="layout"><aside className="sidebar"><div className="side-label">ESPACIO DE TRABAJO</div><button className="nav-item active"><Activity size={17}/> Resolver EDO</button><button className="nav-item" onClick={() => document.getElementById('history')?.scrollIntoView({ behavior: 'smooth' })}><RotateCcw size={17}/> Historial local</button><div className="side-label types-label">MÉTODOS DISPONIBLES</div>{['Lineal de primer orden','Ecuación exacta','Homogénea','Bernoulli reducible'].map((v,i)=><div className="method-item" key={v}><span className="method-num">0{i+1}</span>{v}</div>)}<div className="sidebar-note"><BookOpen size={17}/><div><b>Aprende el método</b><p>Procedimientos simbólicos detallados, paso a paso.</p></div></div></aside>
      <section className="content"><div className="heading"><div><div className="eyebrow"><Sparkles size={14}/> LABORATORIO DE MATEMÁTICAS</div><h1>Resuelve una ecuación</h1><p>Identifica el método y sigue cada transformación matemática.</p></div><button className="help-button"><CircleHelp size={16}/> Guía rápida</button></div>
        <div className="workspace"><div className="workspace-head"><div><span className="section-index">01</span><b>Planteamiento</b></div><div className="segmented"><button className={mode === 'automatico' ? 'selected' : ''} onClick={() => setMode('automatico')}>Automático</button><button className={mode === 'guiado' ? 'selected' : ''} onClick={() => setMode('guiado')}>Modo guiado</button></div></div>
          {mode === 'guiado' && <div className="guided-row"><label>Familia<select value={guided} onChange={e => setGuided(e.target.value)}><option value="lineal">Lineal de primer orden</option><option value="exacta">Exacta</option><option value="homogenea">Homogénea de primer orden</option><option value="bernoulli">Segundo orden reducible a Bernoulli</option></select></label></div>}
          {!(mode === 'guiado' && guided === 'exacta') ? <><div className="editor-label">ECUACIÓN DIFERENCIAL</div><math-field ref={el => { field.current = el as MathField | null }} className="math-editor" onInput={e => setEquation((e.target as MathField).value)} value={equation} virtual-keyboard-mode="manual">{equation}</math-field>
            <div className="symbolbar">{[['x','x'],['y','y'],["y′","y'"],["y″","y''"],['a⁄b','\\frac{#@}{#?}'],['xⁿ','^{}'],['√','\\sqrt{}'],['∫','\\int'],['eˣ','e^{x}'],['ln','\\ln'],['sin','\\sin'],['cos','\\cos'],['π','\\pi'],['∞','\\infty'],['( )','()']].map(([title, token])=><button key={title} onClick={() => insert(token)}>{title}</button>)}</div>
          </> : <div className="exact-fields"><label>M(x,y)<input value={M} onChange={e => setM(e.target.value)}/></label><label>N(x,y)<input value={N} onChange={e => setN(e.target.value)}/></div>}
          <div className="conditions"><div className="condition-title">CONDICIONES INICIALES <span>OPCIONAL</span></div><div className="condition-fields"><label>x₀<input value={x0} onChange={e => setX0(e.target.value)}/></label><label>y(x₀)<input value={y0} onChange={e => setY0(e.target.value)}/>{equation.includes("y''") && <label>y′(x₀)<input value={yp0} onChange={e => setYp0(e.target.value)}/>}</label></div></div>
          <div className="actions"><button className="primary" disabled={busy} onClick={() => solve(false)}>{busy ? 'Resolviendo…' : 'Resolver ecuación'}<ArrowRight size={17}/></button><button className="secondary" disabled={busy} onClick={() => solve(true)}>Identificar</button><button className="clear" onClick={clear}>Limpiar</button></div>
        </div>
        {error && <div className="error">{error}</div>}
        {answer && <section className="result-card"><div className="result-header"><div><div className="result-kicker"><Check size={14}/> ANÁLISIS COMPLETADO</div><h2>Resultado del análisis</h2></div><button className="copy-button" onClick={copy}><Copy size={15}/> Copiar</button></div><div className="metadata"><div><small>FAMILIA IDENTIFICADA</small><b>{labels[answer.tipo_ecuacion] || answer.tipo_ecuacion}</b></div><div><small>MÉTODO</small><b>{labels[answer.metodo] || answer.metodo}</b></div><div><small>ORDEN</small><b>{answer.orden}°</b></div></div>{answer.solucion_latex && <div className="solution"><span className="solution-caption">{answer.tipo_solucion === 'particular' ? 'SOLUCIÓN PARTICULAR' : answer.tipo_solucion === 'implícita' ? 'SOLUCIÓN IMPLÍCITA' : 'SOLUCIÓN GENERAL'}</span><Formula latex={answer.solucion_latex} display/><div className={`verify ${answer.verificacion.estado === 'correcta' ? 'good' : 'neutral'}`}><span>{answer.verificacion.estado === 'correcta' ? '✓' : '·'}</span> Verificación simbólica: {answer.verificacion.estado}</div></div>}
          {answer.pasos.length > 0 && <><button className="steps-toggle" onClick={() => setOpenSteps(!openSteps)}><span><span className="section-index">02</span><b>Procedimiento paso a paso</b><em>{answer.pasos.length} pasos</em></span>{openSteps ? <ChevronDown size={18}/> : <ChevronRight size={18}/>}</button>{openSteps && <div className="steps">{answer.pasos.map(step => <article className="step" key={step.numero}><div className="step-number">{String(step.numero).padStart(2,'0')}</div><div className="step-body"><h3>{step.titulo}</h3><p>{step.explicacion}</p><div className="step-math"><Formula latex={step.expresion_latex} display/></div><div className="reason"><b>Justificación</b>{step.justificacion}</div></div></article>)}</div>}</>}
          {answer.restricciones_dominio?.length ? <div className="domain"><b>Dominio y ramas:</b> {answer.restricciones_dominio.join(' · ')}</div> : null}</section>}
        <section id="history" className="history"><div><h2>Últimas ecuaciones</h2><p>Guardadas únicamente en este dispositivo.</p></div>{history.length ? <div className="history-items">{history.map((item,i)=><button key={i} onClick={() => { setEquation(item); if (field.current) field.current.value=item }}>{item}</button>)}</div> : <span className="empty-history">Aún no hay ecuaciones resueltas.</span>}</section>
        <footer><span>EDO LAB <i>·</i> Herramienta educativa local</span><span>Sin servicios externos</span></footer>
      </section></div>
  </main>
}
