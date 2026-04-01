import type { Metadata } from 'next'
import Link from 'next/link'
import { Inter } from 'next/font/google'
import './globals.css'

// next/font/google — carga optimizada, sin bloqueo de render
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  weight: ['400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'DosificaConcreto | Diseño de Mezclas ACI 211.1 + NSR-10',
  description: 'Herramienta gratuita para diseño de mezclas de concreto según ACI 211.1 y NSR-10. Corrección de humedad, granulometría ASTM C33. Sin registro requerido.',
  keywords: ['diseño de mezclas', 'concreto', 'ACI 211', 'NSR-10', 'Colombia', 'dosificación', 'granulometría', 'ASTM C33'],
  openGraph: {
    title: 'DosificaConcreto | Diseño de Mezclas ACI 211.1 + NSR-10',
    description: 'Herramienta gratuita para ingenieros civiles colombianos. Calcula proporciones ACI 211.1, verifica durabilidad NSR-10, corrige humedad en campo.',
    url: 'https://www.dosificaconcreto.com',
    siteName: 'DosificaConcreto',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'DosificaConcreto — Diseño de Mezclas' }],
    locale: 'es_CO',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DosificaConcreto | ACI 211.1 + NSR-10',
    description: 'Diseño de mezclas de concreto gratis. Colombia.',
    images: ['/og-image.png'],
  },
}

const ConcreteIcon = () => (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="2" y="16" width="24" height="10" rx="2" fill="white" fillOpacity="0.2" stroke="white" strokeWidth="1.5"/>
    <rect x="6" y="10" width="16" height="7" rx="1.5" fill="white" fillOpacity="0.3" stroke="white" strokeWidth="1.5"/>
    <rect x="10" y="4" width="8" height="7" rx="1.5" fill="white" fillOpacity="0.4" stroke="white" strokeWidth="1.5"/>
    <circle cx="7" cy="21" r="1.5" fill="white" fillOpacity="0.6"/>
    <circle cx="14" cy="21" r="1.5" fill="white" fillOpacity="0.6"/>
    <circle cx="21" cy="21" r="1.5" fill="white" fillOpacity="0.6"/>
  </svg>
)

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const year = new Date().getFullYear()

  return (
    <html lang="es" className={inter.className}>
      <body className="min-h-screen flex flex-col bg-slate-50">

        <header style={{ background: 'linear-gradient(135deg, #1a3a5c 0%, #1e4976 100%)' }}
          className="text-white shadow-lg">
          <div className="max-w-6xl mx-auto px-4 py-3.5 flex items-center justify-between">

            <Link href="/" className="flex items-center gap-3 group" aria-label="DosificaConcreto — Inicio">
              <div className="bg-white/10 rounded-lg p-1.5 group-hover:bg-white/20 transition-colors">
                <ConcreteIcon />
              </div>
              <div>
                <div className="font-bold text-lg leading-tight">DosificaConcreto</div>
                <div className="text-xs" style={{ color: 'rgba(255,255,255,0.6)' }}>
                  ACI 211.1 · NSR-10 · Colombia
                </div>
              </div>
            </Link>

            <nav className="hidden sm:flex items-center gap-1" aria-label="Navegación principal">
              <NavLink href="/mezcla" label="Diseño de Mezcla" />
              <NavLink href="/granulometria" label="Granulometría" />
            </nav>

            <div className="flex sm:hidden gap-3 text-xs" aria-label="Navegación móvil">
              <Link href="/mezcla" className="bg-white/10 px-4 py-3 rounded-lg hover:bg-white/20 transition-colors min-h-[44px] flex items-center">
                Mezcla
              </Link>
              <Link href="/granulometria" className="bg-white/10 px-4 py-3 rounded-lg hover:bg-white/20 transition-colors min-h-[44px] flex items-center">
                Granulo.
              </Link>
            </div>

          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="bg-gray-900 text-gray-500 text-xs py-5">
          <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <p>© {year} DosificaConcreto · Comando Construcciones SAS · Bogotá, Colombia</p>
            <p className="text-gray-600">Verificar siempre con ensayos de laboratorio · NTC 396 / NTC 673</p>
          </div>
        </footer>

      </body>
    </html>
  )
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link href={href}
      className="relative px-4 py-2 text-sm font-medium rounded-lg transition-all hover:bg-white/10"
      style={{ color: 'rgba(255,255,255,0.85)' }}>
      {label}
    </Link>
  )
}
