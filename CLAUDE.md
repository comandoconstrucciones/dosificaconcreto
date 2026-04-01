# CLAUDE.md — DosificaConcreto

## Qué es este proyecto

Herramienta web gratuita de **diseño de mezclas de concreto** según **ACI 211.1-91** y **NSR-10** (norma colombiana). Orientada a laboratoristas, ingenieros residentes y estudiantes de ingeniería civil en Colombia.

## Stack técnico

| Capa | Tecnología |
|------|------------|
| Backend | **FastAPI** (Python) — motor de cálculo puro, sin DB |
| Frontend | **Next.js 14** (React 18, TypeScript) |
| Estilos | **Tailwind CSS 3.4** + componentes custom en `globals.css` |
| Gráficas | **Recharts** (curvas granulométricas) |
| HTTP | **Axios** (frontend → API) |
| Deploy | **Vercel** serverless (vercel.json con @vercel/next + @vercel/python) |

## Estructura del proyecto

```
dosificaconcreto/
├── .github/workflows/ci.yml          # GitHub Actions: pytest + lint + build
├── api/index.py                      # Entry point Vercel serverless → FastAPI
├── requirements.txt                  # Dependencias Python
├── backend/
│   ├── main.py                       # FastAPI app: endpoints y schemas Pydantic
│   ├── pytest.ini                    # Configuración pytest
│   ├── calculators/
│   │   ├── aci211.py                 # Motor ACI 211.1 (diseño de mezcla completo)
│   │   └── granulometry.py           # Análisis granulométrico ASTM C33
│   └── tests/
│       ├── conftest.py               # Config path para imports
│       ├── test_aci211.py            # 33 tests ACI 211.1 (pytest)
│       └── test_granulometria.py     # 27 tests granulometría (pytest)
├── frontend/
│   ├── public/robots.txt             # Robots.txt para SEO
│   ├── src/
│   │   ├── components/
│   │   │   ├── Campo.tsx             # Input de formulario reutilizable
│   │   │   ├── ResultCard.tsx        # Tarjeta de resultado
│   │   │   ├── AlertBanner.tsx       # Alerta warning/danger
│   │   │   ├── Badge.tsx             # Badge success/danger
│   │   │   └── ErrorBoundary.tsx     # Error boundary global
│   │   └── app/
│   │       ├── layout.tsx            # Layout raíz (header, nav, footer, OG tags)
│   │       ├── page.tsx              # Home: hero + tarjetas de módulos
│   │       ├── sitemap.ts            # Sitemap dinámico para SEO
│   │       ├── globals.css           # Tailwind + custom component classes
│   │       ├── mezcla/
│   │       │   ├── layout.tsx        # Metadata SEO mezcla
│   │       │   └── page.tsx          # Diseñador de mezcla
│   │       └── granulometria/
│   │           ├── layout.tsx        # Metadata SEO granulometría
│   │           └── page.tsx          # Análisis granulométrico
│   ├── tailwind.config.ts            # Colores: primary (#1a3a5c), accent (#e67e22)
│   └── package.json
├── vercel.json                       # Routing: /api/* → Python, /* → Next.js
├── ROADMAP.md                        # Roadmap del producto
└── CLAUDE.md                         # Este archivo
```

## Comandos esenciales

```bash
# Backend tests
cd backend && python3 tests/test_aci211.py

# Frontend dev
cd frontend && npm install && npm run dev

# Frontend build
cd frontend && npm run build

# Lint
cd frontend && npm run lint
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/mezcla/calcular` | Diseño completo ACI 211.1 |
| POST | `/api/mezcla/corregir-humedad` | Ajuste de campo por humedad |
| GET | `/api/mezcla/valores-tipicos` | Valores default para Bogotá |
| GET | `/api/granulometria/limites/{tipo}` | Límites ASTM C33 (fino/grueso) |
| POST | `/api/granulometria/calcular` | Análisis granulométrico |
| GET | `/api/health` | Health check |

## Arquitectura del motor de cálculo (aci211.py)

Sigue los 7 pasos del método ACI 211.1:
1. **f'cr** — Resistencia requerida promedio (con/sin historial, ACI 318-19)
2. **a/c** — Relación agua/cemento por resistencia + durabilidad NSR-10 (toma el menor)
3. **Agua** — Contenido de agua de mezclado (Tabla 6.3.3: slump × TMS × aire)
4. **Cemento** — agua / a/c (con mínimo por durabilidad)
5. **AG** — Volumen de agregado grueso (Tabla 6.3.6: TMS × módulo finura)
6. **AF** — Por volumen absoluto (1.0 m³ - agua - cemento - AG - aire)
7. **Corrección humedad** — Ajuste laboratorio → campo

## Convenciones

- **Idioma**: código y UI en español (variable names, comments, UI text)
- **Unidades**: kg, m³, MPa (sistema métrico colombiano)
- **No hay DB** — todo es cálculo stateless, sin persistencia
- **No hay auth** — herramienta 100% pública
- **CORS**: `allow_origins=["*"]` para acceso desde cualquier dominio
- **Componentes extraídos** — `Campo`, `ResultCard`, `AlertBanner`, `Badge`, `ErrorBoundary` en `/components`
- **Tests**: pytest framework, ejecutar con `python3 -m pytest tests/ -v` desde `/backend`
- **CI**: GitHub Actions en `.github/workflows/ci.yml` (backend tests + frontend lint/build)
- **Path alias**: `@/*` → `src/*` configurado en tsconfig.json

## Estado actual (v1.0.1)

### Funcionando correctamente
- Motor ACI 211.1 completo con los 7 pasos
- Cálculo f'cr con y sin historial estadístico
- Verificación durabilidad NSR-10 (12 clases de exposición)
- Corrección humedad laboratorio → campo
- Sliders de humedad en tiempo real (recalcula vía API)
- Granulometría fino y grueso con cumplimiento ASTM C33
- Curva granulométrica con Recharts (eje log)
- Módulo de finura automático
- Suma de volúmenes valida a 1.000 m³ exacto
- 60 tests pasan (ACI 211.1 + granulometría + clases exposición + corrección humedad)
- Frontend build exitoso
- Deploy Vercel funcional
- GitHub Actions CI configurado
- SEO: sitemap.xml, robots.txt, Open Graph, meta descriptions por página
- Componentes UI extraídos y reutilizables
- Error Boundary global
- Accesibilidad: aria-labels en formularios
- Validación backend de suma de retenidos

### Deuda técnica restante
- 1 vulnerabilidad npm (high) en `next` — requiere Next.js 16 (breaking change)
- CORS abierto (`*`) — aceptable para v1 pero revisar en producción
- No hay ESLint config personalizado (usa defaults de Next.js)
