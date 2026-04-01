import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Granulometría Combinada — Curva fino + grueso',
  description: 'Análisis granulométrico combinado fino + grueso con verificación de zona óptima ICONTEC. Calcula porcentaje óptimo de combinación.',
  openGraph: {
    title: 'Granulometría Combinada — DosificaConcreto',
    description: 'Curva granulométrica combinada fino + grueso con zona óptima ICONTEC.',
  },
}

export default function CombinedLayout({ children }: { children: React.ReactNode }) {
  return children
}
