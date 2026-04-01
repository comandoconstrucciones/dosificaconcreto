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
├── api/index.py                      # Entry point Vercel serverless → FastAPI
├── backend/
│   ├── main.py                       # FastAPI app: endpoints y schemas Pydantic
│   ├── calculators/
│   │   ├── aci211.py                 # Motor ACI 211.1 (diseño de mezcla completo)
│   │   └── granulometry.py           # Análisis granulométrico ASTM C33
│   └── tests/
│       └── test_aci211.py            # 5 test cases (pytest-compatible, ejecutables directo)
├── frontend/
│   ├── src/app/
│   │   ├── layout.tsx                # Layout raíz (header, nav, footer)
│   │   ├── page.tsx                  # Home: hero + tarjetas de módulos
│   │   ├── globals.css               # Tailwind + custom component classes
│   │   ├── mezcla/page.tsx           # Diseñador de mezcla (formulario + resultados)
│   │   └── granulometria/page.tsx    # Análisis granulométrico (tabla + gráfica)
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
- **Componentes inline** — no hay carpeta `/components`; los helpers (`Campo`, `ResultCard`) están definidos dentro de los page files
- **Tests**: no usan pytest como framework, se ejecutan con `python3` directamente (assertions + prints)

## Estado actual (v1.0)

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
- 5 test cases pasan (f'cr, caso típico, alta resistencia, slump alto, volúmenes)
- Frontend build exitoso
- Deploy Vercel funcional

### Problemas y deuda técnica identificados
- Tests no usan framework (pytest) — no hay CI que los ejecute automáticamente
- No hay tests para el módulo de granulometría
- No hay validación de que `retenidos_pct` sume 100% en el backend (solo frontend)
- Componentes UI monolíticos (todo en page.tsx, no extraídos a /components)
- No hay `requirements.txt` ni `pyproject.toml` para dependencias Python
- No hay ESLint config personalizado
- Sin SEO avanzado (no hay sitemap.xml, robots.txt, Open Graph tags)
- El `handleChange` del formulario tiene un parsing de tipos frágil (`isNaN` + fallback)
- CORS abierto (`*`) — aceptable para v1 pero revisar en producción
- 2 vulnerabilidades npm (1 moderate, 1 high) — ejecutar `npm audit fix`
