import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Análisis Granulométrico ASTM C33',
  description: 'Análisis granulométrico de agregados fino y grueso con verificación de límites ASTM C33 / NTC 174. Curva granulométrica y módulo de finura.',
  openGraph: {
    title: 'Análisis Granulométrico ASTM C33 — DosificaConcreto',
    description: 'Análisis granulométrico con verificación ASTM C33 / NTC 174. Curva granulométrica y módulo de finura.',
  },
}

export default function GranulometriaLayout({ children }: { children: React.ReactNode }) {
  return children
}
