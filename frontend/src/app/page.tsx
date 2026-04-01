import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">

      {/* Hero */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-primary mb-4">
          Diseño de Mezclas de Concreto
        </h1>
        <p className="text-lg text-gray-600 mb-4">
          Herramienta técnica según <strong>ACI 211.1</strong> y <strong>NSR-10</strong>
        </p>
        <div className="inline-flex items-center gap-2 bg-green-50 text-green-700 border border-green-200 px-4 py-2 rounded-full text-sm font-medium">
          <span>✓</span> 100% gratuito · Sin registro · Hecha para Colombia
        </div>
      </div>

      {/* Módulos */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">

        <Link href="/mezcla" className="group">
          <div className="card hover:border-primary hover:shadow-md transition-all h-full">
            <div className="text-4xl mb-4">🧮</div>
            <h2 className="text-xl font-bold text-primary mb-2">Diseño de Mezcla</h2>
            <p className="text-gray-600 text-sm mb-4">
              Proporciones por el método ACI 211.1. Calcula cemento, agua, agregados.
              Verifica durabilidad según clase de exposición NSR-10.
            </p>
            <ul className="text-sm text-gray-500 space-y-1 mb-4">
              <li>✓ f&apos;cr con o sin historial estadístico</li>
              <li>✓ Corrección de humedad en tiempo real</li>
              <li>✓ Verificación NSR-10 C.4 (durabilidad)</li>
              <li>✓ Proporciones laboratorio y campo</li>
            </ul>
            <span className="text-primary font-medium text-sm group-hover:underline">
              Calcular mezcla →
            </span>
          </div>
        </Link>

        <Link href="/granulometria" className="group">
          <div className="card hover:border-primary hover:shadow-md transition-all h-full">
            <div className="text-4xl mb-4">📊</div>
            <h2 className="text-xl font-bold text-primary mb-2">Granulometría</h2>
            <p className="text-gray-600 text-sm mb-4">
              Curva granulométrica de agregado fino y grueso con verificación
              de límites ASTM C33 / NTC 174.
            </p>
            <ul className="text-sm text-gray-500 space-y-1 mb-4">
              <li>✓ Agregado fino y grueso</li>
              <li>✓ Módulo de finura automático</li>
              <li>✓ Límites ASTM C33 por tamiz</li>
              <li>✓ Gráfica con curva y límites</li>
            </ul>
            <span className="text-primary font-medium text-sm group-hover:underline">
              Analizar muestra →
            </span>
          </div>
        </Link>

        <Link href="/granulometria/combinada" className="group">
          <div className="card hover:border-primary hover:shadow-md transition-all h-full">
            <div className="text-4xl mb-4">🔀</div>
            <h2 className="text-xl font-bold text-primary mb-2">Combinada</h2>
            <p className="text-gray-600 text-sm mb-4">
              Curva granulométrica combinada fino + grueso con zona óptima
              para verificar gradación de la mezcla.
            </p>
            <ul className="text-sm text-gray-500 space-y-1 mb-4">
              <li>✓ Combinación fino + grueso</li>
              <li>✓ Zona óptima ICONTEC</li>
              <li>✓ % fino óptimo sugerido</li>
              <li>✓ Exportar curva como PNG</li>
            </ul>
            <span className="text-primary font-medium text-sm group-hover:underline">
              Analizar combinada →
            </span>
          </div>
        </Link>
      </div>

      {/* Nota técnica */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-sm text-blue-800">
        <h3 className="font-semibold mb-2">⚠️ Nota técnica</h3>
        <p>
          Esta herramienta implementa el método ACI 211.1-91 y los requisitos de durabilidad
          de la NSR-10 Capítulo C.4/C.5. Los resultados son de referencia —
          <strong> siempre verifique con ensayos de laboratorio</strong> (NTC 396, NTC 673)
          antes de usar en obra.
        </p>
      </div>
    </div>
  )
}
