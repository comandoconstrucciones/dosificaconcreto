import type { Metadata } from 'next'
import Link from 'next/link'
import './globals.css'

export const metadata: Metadata = {
  title: 'DosificaConcreto | Diseño de Mezclas ACI 211.1 + NSR-10',
  description: 'Herramienta gratuita para diseño de mezclas de concreto según ACI 211.1 y NSR-10. Corrección de humedad, granulometría ASTM C33. Sin registro.',
  keywords: ['diseño de mezclas', 'concreto', 'ACI 211', 'NSR-10', 'Colombia', 'dosificación'],
}

// Ícono SVG de concreto/construcción
const ConcreteIcon = () => (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="16" width="24" height="10" rx="2" fill="white" fillOpacity="0.2" stroke="white" strokeWidth="1.5"/>
    <rect x="6" y="10" width="16" height="7" rx="1.5" fill="white" fillOpacity="0.3" stroke="white" strokeWidth="1.5"/>
    <rect x="10" y="4" width="8" height="7" rx="1.5" fill="white" fillOpacity="0.4" stroke="white" strokeWidth="1.5"/>
    <circle cx="7" cy="21" r="1.5" fill="white" fillOpacity="0.6"/>
    <circle cx="14" cy="21" r="1.5" fill="white" fillOpacity="0.6"/>
    <circle cx="21" cy="21" r="1.5" fill="white" fillOpacity="0.6"/>
  </svg>
)

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen flex flex-col bg-slate-50">

        {/* ── Header ── */}
        <header style={{ background: 'linear-gradient(135deg, #1a3a5c 0%, #1e4976 100%)' }}
          className="text-white shadow-lg">
          <div className="max-w-6xl mx-auto px-4 py-3.5 flex items-center justify-between">

            <Link href="/" className="flex items-center gap-3 group">
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

            <nav className="hidden sm:flex items-center gap-1">
              <NavLink href="/mezcla" label="Diseño de Mezcla" />
              <NavLink href="/granulometria" label="Granulometría" />
            </nav>

            {/* Menú móvil simplificado */}
            <div className="flex sm:hidden gap-3 text-xs">
              <Link href="/mezcla" className="bg-white/10 px-3 py-1.5 rounded-lg hover:bg-white/20 transition-colors">
                Mezcla
              </Link>
              <Link href="/granulometria" className="bg-white/10 px-3 py-1.5 rounded-lg hover:bg-white/20 transition-colors">
                Granulo.
              </Link>
            </div>

          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="bg-gray-900 text-gray-500 text-xs py-5">
          <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <p>© 2026 DosificaConcreto · Comando Construcciones SAS · Bogotá, Colombia</p>
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
