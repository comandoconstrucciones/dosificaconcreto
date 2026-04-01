import Link from 'next/link'

// Íconos SVG inline (no emojis)
const CalcIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="4" width="32" height="32" rx="8" fill="#EEF2FF"/>
    <rect x="10" y="10" width="20" height="20" rx="3" stroke="#1a3a5c" strokeWidth="1.5"/>
    <path d="M14 20h12M20 14v12" stroke="#1a3a5c" strokeWidth="1.5" strokeLinecap="round"/>
    <circle cx="14" cy="14" r="1.5" fill="#e67e22"/>
    <circle cx="26" cy="14" r="1.5" fill="#e67e22"/>
    <circle cx="14" cy="26" r="1.5" fill="#e67e22"/>
    <circle cx="26" cy="26" r="1.5" fill="#e67e22"/>
  </svg>
)

const ChartIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="4" width="32" height="32" rx="8" fill="#F0FDF4"/>
    <path d="M10 28 L16 20 L22 23 L30 12" stroke="#1a3a5c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M10 28 L16 20 L22 23 L30 12" stroke="#27ae60" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="2 2"/>
    <path d="M10 22 L30 22" stroke="#e74c3c" strokeWidth="1" strokeDasharray="3 2" opacity="0.5"/>
    <path d="M10 16 L30 16" stroke="#27ae60" strokeWidth="1" strokeDasharray="3 2" opacity="0.5"/>
  </svg>
)

const CheckIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="10" fill="#27ae60"/>
    <path d="M6 10l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const WaterIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M12 2C12 2 5 9 5 14a7 7 0 0014 0c0-5-7-12-7-12z" stroke="#1a3a5c" strokeWidth="1.5" fill="#EEF2FF"/>
  </svg>
)

const ShieldIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M12 2L4 6v6c0 5 3.5 9.7 8 11 4.5-1.3 8-6 8-11V6l-8-4z" stroke="#1a3a5c" strokeWidth="1.5" fill="#EEF2FF"/>
    <path d="M9 12l2 2 4-4" stroke="#27ae60" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
)

const FreeIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="10" stroke="#1a3a5c" strokeWidth="1.5" fill="#EEF2FF"/>
    <path d="M8 12h8M12 8v8" stroke="#27ae60" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
)

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-10">

      {/* ── Hero ── */}
      <div className="text-center mb-14" style={{ animation: 'fadeIn 0.5s ease forwards' }}>
        <div className="inline-flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-1.5 rounded-full text-xs font-semibold mb-6 uppercase tracking-wide">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse inline-block"></span>
          100% Gratuito · Sin registro · Hecha para Colombia
        </div>

        <h1 className="text-3xl sm:text-4xl font-bold mb-4 leading-tight" style={{ color: '#1a3a5c' }}>
          Diseño de Mezclas de Concreto
        </h1>
        <p className="text-lg text-gray-500 max-w-xl mx-auto mb-8">
          Herramienta técnica según <strong className="text-gray-700">ACI 211.1</strong> y <strong className="text-gray-700">NSR-10</strong> — con corrección de humedad en tiempo real y verificación de durabilidad
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/mezcla">
            <span className="btn-accent px-8 py-3 text-base rounded-xl inline-flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="1" y="1" width="16" height="16" rx="3" stroke="white" strokeWidth="1.5"/>
                <path d="M5 9h8M9 5v8" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              Calcular Mezcla
            </span>
          </Link>
          <Link href="/granulometria">
            <span className="btn-secondary px-8 py-3 text-base rounded-xl inline-flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M2 14L5 9l4 2 7-7" stroke="#1a3a5c" strokeWidth="1.5" strokeLinecap="round"/>
                <path d="M2 10L18 10" stroke="#9ca3af" strokeWidth="1" strokeDasharray="2 2"/>
              </svg>
              Análisis Granulométrico
            </span>
          </Link>
        </div>
      </div>

      {/* ── Módulos ── */}
      <div className="grid md:grid-cols-2 gap-6 mb-14">
        <Link href="/mezcla" className="group">
          <div className="card-accent hover:shadow-lg transition-all h-full cursor-pointer" style={{ borderLeftColor: '#1a3a5c' }}>
            <div className="mb-4"><CalcIcon /></div>
            <h2 className="text-lg font-bold mb-2" style={{ color: '#1a3a5c' }}>Diseño de Mezcla ACI 211.1</h2>
            <p className="text-gray-500 text-sm mb-4">
              Proporciones completas por el método ACI 211.1. Verifica durabilidad según clase de exposición NSR-10.
            </p>
            <ul className="space-y-2 mb-4">
              {[
                "f'cr con o sin historial estadístico",
                "Corrección de humedad en tiempo real",
                "Verificación NSR-10 C.4 (durabilidad)",
                "Proporciones laboratorio y campo",
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                  <CheckIcon />{item}
                </li>
              ))}
            </ul>
            <span className="text-sm font-semibold group-hover:underline" style={{ color: '#1a3a5c' }}>
              Calcular mezcla →
            </span>
          </div>
        </Link>

        <Link href="/granulometria" className="group">
          <div className="card-accent hover:shadow-lg transition-all h-full cursor-pointer" style={{ borderLeftColor: '#27ae60' }}>
            <div className="mb-4"><ChartIcon /></div>
            <h2 className="text-lg font-bold mb-2" style={{ color: '#1a3a5c' }}>Análisis Granulométrico</h2>
            <p className="text-gray-500 text-sm mb-4">
              Curva granulométrica de agregado fino y grueso con verificación de límites ASTM C33 / NTC 174.
            </p>
            <ul className="space-y-2 mb-4">
              {[
                "Agregado fino y grueso",
                "Módulo de finura automático",
                "Límites ASTM C33 por tamiz",
                "Gráfica con curva y límites",
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                  <CheckIcon />{item}
                </li>
              ))}
            </ul>
            <span className="text-sm font-semibold group-hover:underline" style={{ color: '#27ae60' }}>
              Analizar muestra →
            </span>
          </div>
        </Link>
      </div>

      {/* ── Por qué DosificaConcreto ── */}
      <div className="mb-12">
        <h2 className="text-xl font-bold text-center mb-8" style={{ color: '#1a3a5c' }}>
          ¿Por qué es diferente?
        </h2>
        <div className="grid sm:grid-cols-3 gap-5">
          {[
            {
              icon: <WaterIcon />,
              title: "Corrección de humedad",
              desc: "El 80% de las obras ajustan mal el agua. Esta herramienta calcula automáticamente el agua de campo con los sliders.",
              color: "#1a3a5c",
            },
            {
              icon: <ShieldIcon />,
              title: "Durabilidad NSR-10",
              desc: "Verifica la relación a/c mínima y el contenido de cemento según la clase de exposición del NSR-10 C.4.2.",
              color: "#27ae60",
            },
            {
              icon: <FreeIcon />,
              title: "Completamente gratis",
              desc: "Sin registro, sin cuenta, sin límites. Funciona en el celular desde la obra.",
              color: "#e67e22",
            },
          ].map((item, i) => (
            <div key={i} className="card text-center">
              <div className="flex justify-center mb-3">{item.icon}</div>
              <h3 className="font-bold text-sm mb-2" style={{ color: item.color }}>{item.title}</h3>
              <p className="text-xs text-gray-500 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Nota técnica ── */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-5 text-sm text-blue-800">
        <div className="flex items-start gap-3">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="shrink-0 mt-0.5">
            <circle cx="10" cy="10" r="9" stroke="#3b82f6" strokeWidth="1.5"/>
            <path d="M10 9v5M10 7v1" stroke="#3b82f6" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <p>
            Implementa ACI 211.1-91 y NSR-10 C.4/C.5.
            Los resultados son de referencia — <strong>verifique siempre con ensayos de laboratorio</strong> (NTC 396, NTC 673) antes de usar en obra.
          </p>
        </div>
      </div>

    </div>
  )
}
