import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Diseño de Mezcla ACI 211.1',
  description: 'Calculadora de diseño de mezclas de concreto según ACI 211.1. Proporciones de cemento, agua y agregados con verificación de durabilidad NSR-10.',
  openGraph: {
    title: 'Diseño de Mezcla ACI 211.1 — DosificaConcreto',
    description: 'Calculadora de diseño de mezclas de concreto según ACI 211.1 con verificación NSR-10.',
  },
}

export default function MezclaLayout({ children }: { children: React.ReactNode }) {
  return children
}
