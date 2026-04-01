import type { Metadata } from 'next'
import ErrorBoundary from '@/components/ErrorBoundary'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'DosificaConcreto | Diseño de Mezclas ACI 211.1 + NSR-10',
    template: '%s | DosificaConcreto',
  },
  description: 'Herramienta gratuita para diseño de mezclas de concreto según ACI 211.1 y NSR-10. Corrección de humedad, granulometría ASTM C33. Sin registro.',
  keywords: ['diseño de mezclas', 'concreto', 'ACI 211', 'NSR-10', 'Colombia', 'dosificación', 'ingeniería civil', 'ASTM C33'],
  metadataBase: new URL('https://dosificaconcreto.vercel.app'),
  openGraph: {
    title: 'DosificaConcreto — Diseño de Mezclas de Concreto',
    description: 'Herramienta gratuita de diseño de mezclas ACI 211.1 con verificación NSR-10. Para ingenieros y laboratoristas en Colombia.',
    url: 'https://dosificaconcreto.vercel.app',
    siteName: 'DosificaConcreto',
    locale: 'es_CO',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DosificaConcreto — Diseño de Mezclas ACI 211.1',
    description: 'Herramienta gratuita de diseño de mezclas de concreto para Colombia. ACI 211.1 + NSR-10.',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="min-h-screen flex flex-col">
        <header className="bg-primary text-white shadow-md">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2">
              <span className="text-2xl">🏗️</span>
              <div>
                <div className="font-bold text-lg leading-none">DosificaConcreto</div>
                <div className="text-xs text-blue-200">ACI 211.1 · NSR-10 · Colombia</div>
              </div>
            </a>
            <nav className="hidden sm:flex gap-6 text-sm">
              <a href="/mezcla" className="hover:text-accent transition-colors">Diseño de Mezcla</a>
              <a href="/granulometria" className="hover:text-accent transition-colors">Granulometría</a>
              <a href="/granulometria/combinada" className="hover:text-accent transition-colors">Combinada</a>
            </nav>
          </div>
        </header>

        <main className="flex-1">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>

        <footer className="bg-gray-800 text-gray-400 text-xs text-center py-4">
          <p>DosificaConcreto · Comando Construcciones SAS · Bogotá, Colombia</p>
          <p className="mt-1">Herramienta de referencia — verificar siempre con ensayos de laboratorio</p>
        </footer>
      </body>
    </html>
  )
}
