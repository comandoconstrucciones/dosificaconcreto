# DosificaConcreto 🏗️

Herramienta web gratuita para diseño de mezclas de concreto según **ACI 211.1** y **NSR-10**.

## ¿Qué hace?

- Diseño completo de mezclas por el método ACI 211.1
- Resistencia requerida f'cr (con o sin historial estadístico)
- Verificación de durabilidad según clase de exposición (NSR-10 C.4)
- Corrección por humedad de agregados en campo
- Curva granulométrica vs límites ASTM C33
- Exportación de memoria de cálculo en PDF

## Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Next.js 14 (React)
- **Deploy:** Vercel

## Estructura

```
dosificaconcreto/
├── backend/
│   ├── calculators/
│   │   └── aci211.py       ← Motor ACI 211.1 completo
│   └── tests/
│       └── test_aci211.py  ← Tests validados
└── frontend/               ← Next.js (próximamente)
```

## Ejecutar tests

```bash
cd backend
python3 tests/test_aci211.py
```

## Normativa

- ACI 211.1-91 (Reapproved 2009) — Standard Practice for Selecting Proportions for Normal Weight Concrete
- ACI 318-19 — Tabla 5.3.2.2 (f'cr sin historial)
- NSR-10 Capítulo C.4 / C.5 — Requisitos de durabilidad y resistencia

## Autor

Leonardo Ríos — Comando Construcciones SAS  
Bogotá, Colombia
