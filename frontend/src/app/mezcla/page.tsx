'use client'

import { useState, useCallback } from 'react'
import axios from 'axios'

// ─── TIPOS ───────────────────────────────────────────────────────────────────

interface FormData {
  fc_especificado: number
  slump_mm: number
  tms_mm: number
  ge_ag_ssd: number
  absorcion_ag: number
  humedad_ag: number
  peso_unitario_ag: number
  ge_af_ssd: number
  absorcion_af: number
  humedad_af: number
  modulo_finura: number
  tipo_cemento: string
  clase_exposicion: string
  desv_estandar: string
  n_muestras: number
}

interface Resultado {
  fc_especificado: number
  fcr: number
  wc_resistencia: number
  wc_durabilidad: number | null
  wc_diseno: number
  agua_lab: number
  cemento: number
  bultos_cemento: number
  ag_grueso_ssd: number
  ag_fino_ssd: number
  aire_pct: number
  agua_campo: number
  ag_grueso_campo: number
  ag_fino_campo: number
  proporcion_fino: number
  proporcion_grueso: number
  cumple_durabilidad: boolean
  alertas: string[]
}

// ─── DEFAULTS Colombia ────────────────────────────────────────────────────────

const DEFAULTS: FormData = {
  fc_especificado: 21,
  slump_mm: 90,
  tms_mm: 19,
  ge_ag_ssd: 2.65,
  absorcion_ag: 1.0,
  humedad_ag: 2.0,
  peso_unitario_ag: 1580,
  ge_af_ssd: 2.60,
  absorcion_af: 1.5,
  humedad_af: 3.5,
  modulo_finura: 2.80,
  tipo_cemento: 'I',
  clase_exposicion: 'S0',
  desv_estandar: '',
  n_muestras: 0,
}

// ─── COMPONENTES AUXILIARES ──────────────────────────────────────────────────

function Campo({ label, name, value, onChange, type = 'number', step = '0.01', min, max, children }: {
  label: string
  name: string
  value: string | number
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
  type?: string
  step?: string
  min?: string
  max?: string
  children?: React.ReactNode
}) {
  return (
    <div>
      <label className="label">{label}</label>
      {children || (
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          step={step}
          min={min}
          max={max}
          className="input-field"
        />
      )}
    </div>
  )
}

function ResultCard({ label, value, unit, sub }: {
  label: string; value: string | number; unit?: string; sub?: string
}) {
  return (
    <div className="result-card">
      <div className="text-xs text-blue-200 mb-1">{label}</div>
      <div className="text-2xl font-bold">
        {value} <span className="text-sm font-normal">{unit}</span>
      </div>
      {sub && <div className="text-xs text-blue-200 mt-1">{sub}</div>}
    </div>
  )
}

// ─── PÁGINA PRINCIPAL ────────────────────────────────────────────────────────

export default function MezclePage() {
  const [form, setForm] = useState<FormData>(DEFAULTS)
  const [resultado, setResultado] = useState<Resultado | null>(null)
  const [inputOriginal, setInputOriginal] = useState<FormData | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const [humAG, setHumAG] = useState(2.0)
  const [humAF, setHumAF] = useState(3.5)
  const [campo, setCampo] = useState<{ agua: number; ag: number; af: number } | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: isNaN(Number(value)) ? value : Number(value) || value }))
  }

  const calcular = async () => {
    setCargando(true)
    setError('')
    setResultado(null)
    try {
      const payload = {
        ...form,
        desv_estandar: form.desv_estandar ? Number(form.desv_estandar) : null,
      }
      const { data } = await axios.post('/api/mezcla/calcular', payload)
      setResultado(data.resultado)
      setInputOriginal(form)
      setHumAG(form.humedad_ag)
      setHumAF(form.humedad_af)
      setCampo({
        agua: data.resultado.agua_campo,
        ag: data.resultado.ag_grueso_campo,
        af: data.resultado.ag_fino_campo,
      })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Error al calcular. Verifique los datos.')
    } finally {
      setCargando(false)
    }
  }

  const corregirHumedad = useCallback(async (newHumAG: number, newHumAF: number) => {
    if (!resultado || !inputOriginal) return
    try {
      const { data } = await axios.post('/api/mezcla/corregir-humedad', {
        resultado,
        inp: {
          ...inputOriginal,
          desv_estandar: inputOriginal.desv_estandar ? Number(inputOriginal.desv_estandar) : null,
        },
        humedad_ag_campo: newHumAG,
        humedad_af_campo: newHumAF,
      })
      setCampo({
        agua: data.ajuste.agua_campo,
        ag: data.ajuste.ag_grueso_campo,
        af: data.ajuste.ag_fino_campo,
      })
    } catch { /* silencioso */ }
  }, [resultado, inputOriginal])

  const handleHumAG = (v: number) => {
    setHumAG(v)
    corregirHumedad(v, humAF)
  }
  const handleHumAF = (v: number) => {
    setHumAF(v)
    corregirHumedad(humAG, v)
  }

  const limpiar = () => {
    setForm(DEFAULTS)
    setResultado(null)
    setError('')
    setCampo(null)
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">Diseño de Mezcla ACI 211.1</h1>
        <p className="text-sm text-gray-500 mt-1">
          Ingrese los datos de los materiales del laboratorio
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* ── FORMULARIO ── */}
        <div className="space-y-4">

          {/* Resistencia */}
          <div className="card">
            <h3 className="font-semibold text-primary mb-4">1. Resistencia y trabajabilidad</h3>
            <div className="grid grid-cols-2 gap-3">
              <Campo label="f'c especificado (MPa)" name="fc_especificado" value={form.fc_especificado} onChange={handleChange} min="10" max="70" step="1" />
              <Campo label="Slump (mm)" name="slump_mm" value={form.slump_mm} onChange={handleChange} min="25" max="200" step="5" />
              <div className="col-span-2">
                <label className="label">Tamaño máx. nominal (mm)</label>
                <select name="tms_mm" value={form.tms_mm} onChange={handleChange} className="input-field">
                  <option value="9.5">9.5 mm (3/8")</option>
                  <option value="12.5">12.5 mm (1/2")</option>
                  <option value="19">19.0 mm (3/4") — más común</option>
                  <option value="25">25.0 mm (1")</option>
                  <option value="37.5">37.5 mm (1.5")</option>
                </select>
              </div>
            </div>
          </div>

          {/* Agregado grueso */}
          <div className="card">
            <h3 className="font-semibold text-primary mb-4">2. Agregado grueso</h3>
            <div className="grid grid-cols-2 gap-3">
              <Campo label="Gravedad esp. SSD" name="ge_ag_ssd" value={form.ge_ag_ssd} onChange={handleChange} step="0.01" />
              <Campo label="Absorción (%)" name="absorcion_ag" value={form.absorcion_ag} onChange={handleChange} step="0.1" />
              <Campo label="Humedad superficial (%)" name="humedad_ag" value={form.humedad_ag} onChange={handleChange} step="0.1" />
              <Campo label="Peso unitario suelto (kg/m³)" name="peso_unitario_ag" value={form.peso_unitario_ag} onChange={handleChange} step="10" />
            </div>
          </div>

          {/* Agregado fino */}
          <div className="card">
            <h3 className="font-semibold text-primary mb-4">3. Agregado fino</h3>
            <div className="grid grid-cols-2 gap-3">
              <Campo label="Gravedad esp. SSD" name="ge_af_ssd" value={form.ge_af_ssd} onChange={handleChange} step="0.01" />
              <Campo label="Absorción (%)" name="absorcion_af" value={form.absorcion_af} onChange={handleChange} step="0.1" />
              <Campo label="Humedad superficial (%)" name="humedad_af" value={form.humedad_af} onChange={handleChange} step="0.1" />
              <Campo label="Módulo de finura" name="modulo_finura" value={form.modulo_finura} onChange={handleChange} step="0.01" />
            </div>
          </div>

          {/* Cemento y exposición */}
          <div className="card">
            <h3 className="font-semibold text-primary mb-4">4. Cemento y exposición</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Tipo de cemento</label>
                <select name="tipo_cemento" value={form.tipo_cemento} onChange={handleChange} className="input-field">
                  <option value="I">Tipo I (uso general)</option>
                  <option value="II">Tipo II (moderado)</option>
                  <option value="III">Tipo III (alta resistencia)</option>
                  <option value="IV">Tipo IV (bajo calor)</option>
                  <option value="V">Tipo V (sulfato-resistente)</option>
                  <option value="IP">Tipo IP (puzolánico)</option>
                </select>
              </div>
              <div>
                <label className="label">Clase de exposición NSR-10</label>
                <select name="clase_exposicion" value={form.clase_exposicion} onChange={handleChange} className="input-field">
                  <optgroup label="Sulfatos">
                    <option value="S0">S0 — Sin exposición</option>
                    <option value="S1">S1 — Moderada</option>
                    <option value="S2">S2 — Severa</option>
                    <option value="S3">S3 — Muy severa</option>
                  </optgroup>
                  <optgroup label="Corrosión refuerzo">
                    <option value="C0">C0 — Sin riesgo</option>
                    <option value="C1">C1 — Exposición moderada</option>
                    <option value="C2">C2 — Exposición severa</option>
                  </optgroup>
                  <optgroup label="Congelación">
                    <option value="F0">F0 — Sin congelación</option>
                    <option value="F1">F1 — Moderada</option>
                    <option value="F2">F2 — Severa</option>
                  </optgroup>
                  <optgroup label="Permeabilidad">
                    <option value="W0">W0 — Sin requisito</option>
                    <option value="W1">W1 — Baja permeabilidad</option>
                    <option value="W2">W2 — Muy baja permeabilidad</option>
                  </optgroup>
                </select>
              </div>
            </div>
          </div>

          {/* Historial (opcional) */}
          <div className="card">
            <h3 className="font-semibold text-primary mb-1">5. Historial estadístico (opcional)</h3>
            <p className="text-xs text-gray-500 mb-3">Si tiene ensayos previos, ingrese la desviación estándar</p>
            <div className="grid grid-cols-2 gap-3">
              <Campo label="Desv. estándar (MPa)" name="desv_estandar" value={form.desv_estandar} onChange={handleChange} step="0.1" type="number" />
              <Campo label="N° de muestras" name="n_muestras" value={form.n_muestras} onChange={handleChange} step="1" type="number" min="0" />
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={calcular} disabled={cargando} className="btn-accent flex-1 text-base py-3">
              {cargando
                ? <><span className="spinner mr-2"></span>Calculando...</>
                : <>Calcular Mezcla</>}
            </button>
            <button onClick={limpiar} className="btn-secondary">Limpiar</button>
          </div>

          {error && <div className="alert-danger">{error}</div>}
        </div>

        {/* ── RESULTADOS ── */}
        <div>
          {resultado ? (
            <div className="space-y-4">
              {/* Alertas */}
              {resultado.alertas.length > 0 && (
                <div className="space-y-2">
                  {resultado.alertas.map((a, i) => (
                    <div key={i} className="alert-warning">⚠️ {a}</div>
                  ))}
                </div>
              )}

              {/* Tarjetas principales */}
              <div className="grid grid-cols-2 gap-3">
                <ResultCard label="Resistencia requerida f'cr" value={resultado.fcr} unit="MPa" />
                <ResultCard label="Relación a/c diseño" value={resultado.wc_diseno} sub={resultado.wc_durabilidad ? `Durabilidad: ≤${resultado.wc_durabilidad}` : undefined} />
                <ResultCard label="Agua de mezclado" value={resultado.agua_lab} unit="kg/m³" />
                <ResultCard label="Cemento" value={resultado.cemento} unit="kg/m³" sub={`${resultado.bultos_cemento} bultos de 50 kg`} />
              </div>

              {/* Tabla Lab vs Campo */}
              <div className="card">
                <h3 className="font-semibold text-primary mb-3">Proporciones por m³</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-gray-500 border-b">
                      <th className="text-left py-2">Material</th>
                      <th className="text-right py-2">Laboratorio</th>
                      <th className="text-right py-2 text-accent">Campo</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    <tr>
                      <td className="py-2">Agua (kg)</td>
                      <td className="text-right font-mono">{resultado.agua_lab}</td>
                      <td className="text-right font-mono text-accent font-semibold">{campo?.agua ?? resultado.agua_campo}</td>
                    </tr>
                    <tr>
                      <td className="py-2">Cemento (kg)</td>
                      <td className="text-right font-mono">{resultado.cemento}</td>
                      <td className="text-right font-mono text-accent font-semibold">{resultado.cemento}</td>
                    </tr>
                    <tr>
                      <td className="py-2">Ag. Grueso (kg)</td>
                      <td className="text-right font-mono">{resultado.ag_grueso_ssd}</td>
                      <td className="text-right font-mono text-accent font-semibold">{campo?.ag ?? resultado.ag_grueso_campo}</td>
                    </tr>
                    <tr>
                      <td className="py-2">Ag. Fino (kg)</td>
                      <td className="text-right font-mono">{resultado.ag_fino_ssd}</td>
                      <td className="text-right font-mono text-accent font-semibold">{campo?.af ?? resultado.ag_fino_campo}</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="py-2 font-medium">Aire atrapado</td>
                      <td className="text-right font-mono" colSpan={2}>{resultado.aire_pct}%</td>
                    </tr>
                  </tbody>
                </table>

                <div className="mt-3 pt-3 border-t text-sm text-gray-600">
                  <span className="font-medium">Proporciones en peso: </span>
                  <span className="font-mono font-semibold text-primary">
                    1 : {resultado.proporcion_fino} : {resultado.proporcion_grueso}
                  </span>
                  <span className="text-gray-400 ml-1">(C : AF : AG)</span>
                </div>
              </div>

              {/* Corrección de humedad en tiempo real */}
              <div className="card">
                <h3 className="font-semibold text-primary mb-1">Ajuste de humedad en campo</h3>
                <p className="text-xs text-gray-500 mb-4">Mueva los sliders para actualizar la columna Campo</p>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Humedad AG</span>
                      <span className="font-mono font-semibold">{humAG.toFixed(1)}%</span>
                    </div>
                    <input
                      type="range" min="0" max="10" step="0.5"
                      value={humAG}
                      onChange={e => handleHumAG(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>0%</span><span>10%</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Humedad AF</span>
                      <span className="font-mono font-semibold">{humAF.toFixed(1)}%</span>
                    </div>
                    <input
                      type="range" min="0" max="15" step="0.5"
                      value={humAF}
                      onChange={e => handleHumAF(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>0%</span><span>15%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Cumplimiento durabilidad */}
              <div className="flex items-center gap-2">
                {resultado.cumple_durabilidad
                  ? <span className="badge-success">✓ Cumple durabilidad NSR-10</span>
                  : <span className="badge-danger">✗ No cumple durabilidad NSR-10</span>
                }
              </div>
            </div>
          ) : (
            <div className="card h-64 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="text-4xl mb-3">🧪</div>
                <p>Complete el formulario y calcule</p>
                <p className="text-sm mt-1">Los resultados aparecerán aquí</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
