'use client'

import { useState, useRef, useCallback } from 'react'
import axios from 'axios'
import html2canvas from 'html2canvas'
import AlertBanner from '@/components/AlertBanner'
import Badge from '@/components/Badge'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Area
} from 'recharts'

// ─── TIPOS ───────────────────────────────────────────────────────────────────

interface TamizCombinado {
  nombre: string
  abertura_mm: number
  pasa_fino_pct: number
  pasa_grueso_pct: number
  pasa_combinado_pct: number
  zona_inf: number | null
  zona_sup: number | null
  en_zona: boolean | null
}

interface ResultadoCombinado {
  pct_fino: number
  pct_grueso: number
  pct_fino_optimo: number
  en_zona_optima: boolean
  fino_cumple_astm: boolean
  grueso_cumple_astm: boolean
  modulo_finura: number | null
  alertas: string[]
  tamices: TamizCombinado[]
}

// ─── DATOS ────────────────────────────────────────────────────────────────────

const TAMICES_FINO = [
  '9.5mm (3/8")', '4.75mm (#4)', '2.36mm (#8)', '1.18mm (#16)',
  '0.60mm (#30)', '0.30mm (#50)', '0.15mm (#100)', 'Fondo'
]
const TAMICES_GRUESO = [
  '37.5mm (1.5")', '25.0mm (1")', '19.0mm (3/4")', '12.5mm (1/2")',
  '9.5mm (3/8")', '4.75mm (#4)', '2.36mm (#8)', 'Fondo'
]

const DEFAULTS_FINO = [0, 2, 8, 15, 25, 25, 20, 5]
const DEFAULTS_GRUESO = [0, 0, 5, 25, 30, 30, 8, 2]

// ─── PÁGINA ──────────────────────────────────────────────────────────────────

export default function CombinedPage() {
  const [retFino, setRetFino] = useState<number[]>(DEFAULTS_FINO)
  const [retGrueso, setRetGrueso] = useState<number[]>(DEFAULTS_GRUESO)
  const [tms, setTms] = useState(19.0)
  const [pctFino, setPctFino] = useState(40)
  const [resultado, setResultado] = useState<ResultadoCombinado | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const chartRef = useRef<HTMLDivElement>(null)

  const sumaFino = retFino.reduce((a, b) => a + b, 0)
  const sumaGrueso = retGrueso.reduce((a, b) => a + b, 0)
  const sumaFinoOk = Math.abs(sumaFino - 100) < 1.5
  const sumaGruesoOk = Math.abs(sumaGrueso - 100) < 1.5

  const handleRetFino = (i: number, val: string) => {
    const arr = [...retFino]
    arr[i] = parseFloat(val) || 0
    setRetFino(arr)
  }

  const handleRetGrueso = (i: number, val: string) => {
    const arr = [...retGrueso]
    arr[i] = parseFloat(val) || 0
    setRetGrueso(arr)
  }

  const calcular = async () => {
    setCargando(true)
    setError('')
    try {
      const { data } = await axios.post('/api/granulometria/combinada', {
        retenidos_fino: retFino,
        retenidos_grueso: retGrueso,
        tms_mm: tms,
        pct_fino: pctFino,
      })
      setResultado(data.resultado)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Error al calcular')
    } finally {
      setCargando(false)
    }
  }

  const recalcularConPct = useCallback(async (newPct: number) => {
    setPctFino(newPct)
    if (!sumaFinoOk || !sumaGruesoOk) return
    try {
      const { data } = await axios.post('/api/granulometria/combinada', {
        retenidos_fino: retFino,
        retenidos_grueso: retGrueso,
        tms_mm: tms,
        pct_fino: newPct,
      })
      setResultado(data.resultado)
    } catch { /* silencioso */ }
  }, [retFino, retGrueso, tms, sumaFinoOk, sumaGruesoOk])

  const exportarPNG = async () => {
    if (!chartRef.current) return
    const canvas = await html2canvas(chartRef.current, {
      backgroundColor: '#ffffff',
      scale: 2,
    })
    const link = document.createElement('a')
    link.download = `granulometria-combinada-${pctFino}pct-fino.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }

  // Preparar datos para gráfica
  const datosGrafica = resultado
    ? resultado.tamices
        .map(t => ({
          abertura: t.abertura_mm,
          'Combinado': t.pasa_combinado_pct,
          'Fino': t.pasa_fino_pct,
          'Grueso': t.pasa_grueso_pct,
          'Zona inf.': t.zona_inf,
          'Zona sup.': t.zona_sup,
        }))
        .sort((a, b) => a.abertura - b.abertura)
    : []

  const SumaBadge = ({ suma, ok }: { suma: number; ok: boolean }) => (
    <span className={`text-xs font-mono px-2 py-1 rounded ${
      ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
    }`}>
      {suma.toFixed(1)}% {ok ? '✓' : '!'}
    </span>
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Granulometría Combinada</h1>
        <p className="text-sm text-gray-500 mt-1">
          Curva combinada fino + grueso con zona óptima (ICONTEC / NTC 174)
        </p>
      </div>

      {/* ── ENTRADA: Fino y Grueso lado a lado ── */}
      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        {/* Fino */}
        <div className="card">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-primary">Agregado Fino — % retenido</h3>
            <SumaBadge suma={sumaFino} ok={sumaFinoOk} />
          </div>
          <div className="space-y-1.5">
            {TAMICES_FINO.map((tam, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs text-gray-600 w-28 shrink-0">{tam}</span>
                <input
                  type="number"
                  value={retFino[i] ?? 0}
                  onChange={e => handleRetFino(i, e.target.value)}
                  min="0" max="100" step="0.1"
                  className="input-field text-right font-mono text-sm py-1"
                  aria-label={`% retenido fino en tamiz ${tam}`}
                />
                <span className="text-gray-400 text-xs">%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Grueso */}
        <div className="card">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-primary">Agregado Grueso — % retenido</h3>
            <SumaBadge suma={sumaGrueso} ok={sumaGruesoOk} />
          </div>
          <div className="mb-3">
            <label className="label">TMS (mm)</label>
            <select
              value={tms}
              onChange={e => setTms(Number(e.target.value))}
              className="input-field"
              aria-label="Tamaño máximo nominal grueso"
            >
              <option value="9.5">9.5 mm (3/8")</option>
              <option value="12.5">12.5 mm (1/2")</option>
              <option value="19">19.0 mm (3/4")</option>
              <option value="25">25.0 mm (1")</option>
              <option value="37.5">37.5 mm (1.5")</option>
            </select>
          </div>
          <div className="space-y-1.5">
            {TAMICES_GRUESO.map((tam, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs text-gray-600 w-28 shrink-0">{tam}</span>
                <input
                  type="number"
                  value={retGrueso[i] ?? 0}
                  onChange={e => handleRetGrueso(i, e.target.value)}
                  min="0" max="100" step="0.1"
                  className="input-field text-right font-mono text-sm py-1"
                  aria-label={`% retenido grueso en tamiz ${tam}`}
                />
                <span className="text-gray-400 text-xs">%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Slider % fino + botón calcular */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div className="flex-1 w-full">
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">Proporción de fino en la mezcla</span>
              <span className="font-mono font-bold text-primary">{pctFino}% fino / {100 - pctFino}% grueso</span>
            </div>
            <input
              type="range" min="10" max="70" step="1"
              value={pctFino}
              onChange={e => {
                const v = Number(e.target.value)
                if (resultado) {
                  recalcularConPct(v)
                } else {
                  setPctFino(v)
                }
              }}
              className="w-full accent-primary"
              aria-label="Porcentaje de agregado fino en la mezcla"
            />
            <div className="flex justify-between text-xs text-gray-400">
              <span>10%</span><span>40%</span><span>70%</span>
            </div>
          </div>
          <button
            onClick={calcular}
            disabled={cargando || !sumaFinoOk || !sumaGruesoOk}
            className="btn-primary whitespace-nowrap"
          >
            {cargando ? 'Calculando...' : 'Analizar Combinada'}
          </button>
        </div>
      </div>

      {error && <AlertBanner type="danger">{error}</AlertBanner>}

      {/* ── RESULTADOS ── */}
      {resultado && (
        <div className="space-y-4 print-section">

          {/* Alertas */}
          {resultado.alertas.map((a, i) => (
            <AlertBanner key={i} type="warning">⚠️ {a}</AlertBanner>
          ))}

          {/* Header badges */}
          <div className="flex flex-wrap gap-2">
            {resultado.en_zona_optima
              ? <Badge type="success">✓ En zona óptima</Badge>
              : <Badge type="danger">✗ Fuera de zona óptima</Badge>
            }
            {resultado.fino_cumple_astm
              ? <Badge type="success">✓ Fino cumple ASTM C33</Badge>
              : <Badge type="danger">✗ Fino no cumple ASTM C33</Badge>
            }
            {resultado.grueso_cumple_astm
              ? <Badge type="success">✓ Grueso cumple ASTM C33</Badge>
              : <Badge type="danger">✗ Grueso no cumple ASTM C33</Badge>
            }
            {resultado.modulo_finura !== null && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                MF: {resultado.modulo_finura}
              </span>
            )}
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
              Óptimo sugerido: {resultado.pct_fino_optimo}% fino
            </span>
          </div>

          {/* Gráfica */}
          <div className="card" ref={chartRef}>
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-primary">
                Curva granulométrica combinada ({resultado.pct_fino}% fino / {resultado.pct_grueso}% grueso)
              </h3>
              <button
                onClick={exportarPNG}
                className="btn-secondary text-xs py-1.5 px-3 print:hidden"
              >
                Exportar PNG
              </button>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={datosGrafica} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="abertura"
                  scale="log"
                  domain={['auto', 'auto']}
                  tickFormatter={v => `${v}`}
                  label={{ value: 'Abertura (mm)', position: 'insideBottom', offset: -2, fontSize: 11 }}
                  tick={{ fontSize: 10 }}
                />
                <YAxis
                  domain={[0, 100]}
                  tickFormatter={v => `${v}%`}
                  tick={{ fontSize: 10 }}
                />
                <Tooltip
                  formatter={(v: number, name: string) => [`${v}%`, name]}
                  labelFormatter={v => `Abertura: ${v} mm`}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />

                {/* Zona óptima como área sombreada */}
                <Line
                  type="monotone"
                  dataKey="Zona sup."
                  stroke="#27ae60"
                  strokeWidth={1}
                  strokeDasharray="4 4"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="Zona inf."
                  stroke="#27ae60"
                  strokeWidth={1}
                  strokeDasharray="4 4"
                  dot={false}
                />

                {/* Curva fino */}
                <Line
                  type="monotone"
                  dataKey="Fino"
                  stroke="#3498db"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                />

                {/* Curva grueso */}
                <Line
                  type="monotone"
                  dataKey="Grueso"
                  stroke="#e74c3c"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                />

                {/* Curva combinada (principal) */}
                <Line
                  type="monotone"
                  dataKey="Combinado"
                  stroke="#1a3a5c"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#1a3a5c' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Tabla detalle */}
          <div className="card overflow-x-auto">
            <h3 className="font-semibold text-primary mb-3">Detalle por tamiz</h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-primary text-white">
                  <th className="text-left py-2 px-2 rounded-tl-lg">Tamiz</th>
                  <th className="text-right py-2 px-2">Fino (%)</th>
                  <th className="text-right py-2 px-2">Grueso (%)</th>
                  <th className="text-right py-2 px-2 font-bold">Comb. (%)</th>
                  <th className="text-right py-2 px-2">Zona inf.</th>
                  <th className="text-right py-2 px-2 rounded-tr-lg">Zona sup.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {resultado.tamices.map((t, i) => (
                  <tr
                    key={i}
                    className={
                      t.en_zona === false
                        ? 'bg-red-50'
                        : i % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                    }
                  >
                    <td className="py-1.5 px-2 font-medium">{t.nombre}</td>
                    <td className="text-right py-1.5 px-2 font-mono text-blue-600">{t.pasa_fino_pct}</td>
                    <td className="text-right py-1.5 px-2 font-mono text-red-500">{t.pasa_grueso_pct}</td>
                    <td className="text-right py-1.5 px-2 font-mono font-bold">{t.pasa_combinado_pct}</td>
                    <td className="text-right py-1.5 px-2 text-green-600">{t.zona_inf ?? '—'}</td>
                    <td className="text-right py-1.5 px-2 text-green-600">
                      {t.zona_sup ?? '—'}
                      {t.en_zona === false && <span className="ml-1 text-red-600 font-bold">✗</span>}
                      {t.en_zona === true && <span className="ml-1 text-green-600">✓</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!resultado && !error && (
        <div className="card h-48 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <div className="text-4xl mb-3">📊</div>
            <p>Ingrese los datos de ambos agregados</p>
            <p className="text-sm mt-1">La curva combinada aparecerá aquí</p>
          </div>
        </div>
      )}
    </div>
  )
}
