'use client'

import { useState } from 'react'
import axios from 'axios'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'

// ─── TIPOS ───────────────────────────────────────────────────────────────────

interface TamizResultado {
  nombre: string
  abertura_mm: number
  retenido_pct: number
  retenido_acum_pct: number
  pasa_pct: number
  limite_inf: number | null
  limite_sup: number | null
  cumple: boolean | null
}

interface ResultadoGranulo {
  tipo: string
  tms_mm: number | null
  modulo_finura: number | null
  cumple_astm: boolean
  alertas: string[]
  tamices: TamizResultado[]
}

// ─── TAMICES POR TIPO ─────────────────────────────────────────────────────────

const TAMICES_FINO = [
  '9.5mm (3/8")', '4.75mm (#4)', '2.36mm (#8)', '1.18mm (#16)',
  '0.60mm (#30)', '0.30mm (#50)', '0.15mm (#100)', 'Fondo'
]

const TAMICES_GRUESO = [
  '37.5mm (1.5")', '25.0mm (1")', '19.0mm (3/4")', '12.5mm (1/2")',
  '9.5mm (3/8")', '4.75mm (#4)', '2.36mm (#8)', 'Fondo'
]

const DEFAULTS_FINO   = [0, 2, 8, 15, 25, 25, 20, 5]
const DEFAULTS_GRUESO = [0, 0, 5, 25, 30, 30, 8, 2]

// ─── PÁGINA ──────────────────────────────────────────────────────────────────

export default function GranulometriaPage() {
  const [tipo, setTipo] = useState<'fino' | 'grueso'>('fino')
  const [tms, setTms] = useState(19.0)
  const [retenidos, setRetenidos] = useState<number[]>(DEFAULTS_FINO)
  const [resultado, setResultado] = useState<ResultadoGranulo | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')

  const tamices = tipo === 'fino' ? TAMICES_FINO : TAMICES_GRUESO

  const handleTipo = (t: 'fino' | 'grueso') => {
    setTipo(t)
    setRetenidos(t === 'fino' ? DEFAULTS_FINO : DEFAULTS_GRUESO)
    setResultado(null)
  }

  const handleRetenido = (i: number, val: string) => {
    const arr = [...retenidos]
    arr[i] = parseFloat(val) || 0
    setRetenidos(arr)
  }

  const calcular = async () => {
    setCargando(true)
    setError('')
    try {
      const { data } = await axios.post('/api/granulometria/calcular', {
        tipo,
        tms_mm: tms,
        retenidos_pct: retenidos,
      })
      setResultado(data.resultado)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Error al calcular')
    } finally {
      setCargando(false)
    }
  }

  // Preparar datos para gráfica
  const datosGrafica = resultado
    ? resultado.tamices
        .filter(t => t.abertura_mm > 0)
        .map(t => ({
          abertura: t.abertura_mm,
          'Material (% pasa)': t.pasa_pct,
          'Límite inferior': t.limite_inf,
          'Límite superior': t.limite_sup,
        }))
        .sort((a, b) => a.abertura - b.abertura)
    : []

  // Verificar suma retenidos
  const sumaRetenidos = retenidos.reduce((a, b) => a + b, 0)
  const sumaOk = Math.abs(sumaRetenidos - 100) < 1

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Análisis Granulométrico</h1>
        <p className="text-sm text-gray-500 mt-1">
          Verificación de límites ASTM C33 / NTC 174
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* ── ENTRADA ── */}
        <div className="space-y-4">

          {/* Tipo y TMS */}
          <div className="card">
            <h3 className="font-semibold text-primary mb-3">Tipo de agregado</h3>
            <div className="flex gap-3 mb-4">
              <button
                onClick={() => handleTipo('fino')}
                className={`flex-1 py-2 rounded-lg font-medium text-sm transition-colors ${
                  tipo === 'fino'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Agregado Fino
              </button>
              <button
                onClick={() => handleTipo('grueso')}
                className={`flex-1 py-2 rounded-lg font-medium text-sm transition-colors ${
                  tipo === 'grueso'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Agregado Grueso
              </button>
            </div>

            {tipo === 'grueso' && (
              <div>
                <label className="label">Tamaño máximo nominal (mm)</label>
                <select
                  value={tms}
                  onChange={e => setTms(Number(e.target.value))}
                  className="input-field"
                >
                  <option value="9.5">9.5 mm (3/8")</option>
                  <option value="12.5">12.5 mm (1/2")</option>
                  <option value="19">19.0 mm (3/4")</option>
                  <option value="25">25.0 mm (1")</option>
                  <option value="37.5">37.5 mm (1.5")</option>
                </select>
              </div>
            )}
          </div>

          {/* Tabla de entrada */}
          <div className="card">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-primary">% Retenido por tamiz</h3>
              <span className={`text-xs font-mono px-2 py-1 rounded ${
                sumaOk ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                Σ = {sumaRetenidos.toFixed(1)}% {sumaOk ? '✓' : '≠ 100%'}
              </span>
            </div>

            <div className="space-y-2">
              {tamices.map((tam, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 w-32 shrink-0">{tam}</span>
                  <input
                    type="number"
                    value={retenidos[i] ?? 0}
                    onChange={e => handleRetenido(i, e.target.value)}
                    min="0"
                    max="100"
                    step="0.1"
                    className="input-field text-right font-mono"
                  />
                  <span className="text-gray-400 text-sm shrink-0">%</span>
                </div>
              ))}
            </div>

            {!sumaOk && (
              <p className="text-xs text-red-600 mt-2">
                La suma debe ser 100% ± 1%
              </p>
            )}
          </div>

          <button
            onClick={calcular}
            disabled={cargando || !sumaOk}
            className="btn-primary w-full"
          >
            {cargando ? 'Calculando...' : '📊 Analizar Granulometría'}
          </button>

          {error && <div className="alert-danger">{error}</div>}
        </div>

        {/* ── RESULTADOS ── */}
        <div className="space-y-4">
          {resultado ? (
            <>
              {/* Header resultado */}
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-primary">Resultado</h3>
                  {resultado.cumple_astm
                    ? <span className="badge-success">✓ CUMPLE ASTM C33</span>
                    : <span className="badge-danger">✗ NO CUMPLE ASTM C33</span>
                  }
                </div>

                {resultado.modulo_finura !== null && (
                  <div className="bg-primary text-white rounded-lg p-4 text-center mb-3">
                    <div className="text-xs text-blue-200 mb-1">Módulo de Finura</div>
                    <div className="text-3xl font-bold">{resultado.modulo_finura}</div>
                    <div className="text-xs text-blue-200 mt-1">Rango recomendado: 2.3 – 3.1</div>
                  </div>
                )}

                {resultado.alertas.map((a, i) => (
                  <div key={i} className="alert-warning mt-2">⚠️ {a}</div>
                ))}
              </div>

              {/* Gráfica */}
              {datosGrafica.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-primary mb-3">Curva granulométrica</h3>
                  <ResponsiveContainer width="100%" height={280}>
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
                      <Line
                        type="monotone"
                        dataKey="Material (% pasa)"
                        stroke="#1a3a5c"
                        strokeWidth={2.5}
                        dot={{ r: 4, fill: '#1a3a5c' }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Límite inferior"
                        stroke="#27ae60"
                        strokeWidth={1.5}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="Límite superior"
                        stroke="#e74c3c"
                        strokeWidth={1.5}
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Tabla detalle */}
              <div className="card overflow-x-auto">
                <h3 className="font-semibold text-primary mb-3">Detalle por tamiz</h3>
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-primary text-white">
                      <th className="text-left py-2 px-2 rounded-tl-lg">Tamiz</th>
                      <th className="text-right py-2 px-2">Ret. (%)</th>
                      <th className="text-right py-2 px-2">Ret. Acum. (%)</th>
                      <th className="text-right py-2 px-2">Pasa (%)</th>
                      <th className="text-right py-2 px-2">Lím. Inf.</th>
                      <th className="text-right py-2 px-2 rounded-tr-lg">Lím. Sup.</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {resultado.tamices.map((t, i) => (
                      <tr
                        key={i}
                        className={
                          t.cumple === false
                            ? 'bg-red-50'
                            : i % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                        }
                      >
                        <td className="py-1.5 px-2 font-medium">{t.nombre}</td>
                        <td className="text-right py-1.5 px-2 font-mono">{t.retenido_pct}</td>
                        <td className="text-right py-1.5 px-2 font-mono">{t.retenido_acum_pct}</td>
                        <td className="text-right py-1.5 px-2 font-mono font-semibold">{t.pasa_pct}</td>
                        <td className="text-right py-1.5 px-2 text-green-600">{t.limite_inf ?? '—'}</td>
                        <td className="text-right py-1.5 px-2 text-red-500">
                          {t.limite_sup ?? '—'}
                          {t.cumple === false && (
                            <span className="ml-1 text-red-600 font-bold">✗</span>
                          )}
                          {t.cumple === true && (
                            <span className="ml-1 text-green-600">✓</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="card h-64 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="text-4xl mb-3">📊</div>
                <p>Ingrese los % retenidos y calcule</p>
                <p className="text-sm mt-1">La curva aparecerá aquí</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
