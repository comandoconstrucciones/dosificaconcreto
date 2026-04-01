# DosificaConcreto 🏗️

Calculadora profesional de diseño de mezclas de concreto según **ACI 211.1** y **NSR-10 Colombia**.

## Características

- ✅ Motor ACI 211.1 completo (7 pasos)
- ✅ Resistencia requerida f'cr (con y sin historial estadístico)
- ✅ Verificación de durabilidad NSR-10 C.4/C.5 (exposición F, S, W, C)
- ✅ Corrección por humedad de agregados (laboratorio → campo)
- ✅ Volumen absoluto — suma exacta a 1.000 m³
- 🔜 API FastAPI REST
- 🔜 Frontend Next.js
- 🔜 Curva granulométrica ASTM C33
- 🔜 Exportar informe PDF
- 🔜 Costo por m³ con precios Colombia

## Stack

- **Backend:** Python + FastAPI
- **Frontend:** Next.js 14 (React)
- **Deploy:** Vercel

## Uso rápido (backend)

```python
from backend.calculators.aci211 import diseñar_mezcla, MaterialesInput

inp = MaterialesInput(
    fc_especificado=21.0,
    slump_mm=90,
    tms_mm=19.0,
    ge_ag_ssd=2.68,
    absorcion_ag=0.5,
    humedad_ag=2.0,
    peso_unitario_ag=1600,
    ge_af_ssd=2.64,
    absorcion_af=1.3,
    humedad_af=4.0,
    modulo_finura=2.80,
    tipo_cemento="I",
    clase_exposicion="S0"
)

r = diseñar_mezcla(inp)
print(f"Cemento: {r.cemento} kg/m³")
print(f"Agua (campo): {r.agua_campo} kg/m³")
print(f"AG campo: {r.ag_grueso_campo} kg/m³")
print(f"AF campo: {r.ag_fino_campo} kg/m³")
```

## Tests

```bash
python3 backend/tests/test_aci211.py
```

## Normativa

- ACI 211.1-91 (Reapproved 2009) — Standard Practice for Selecting Proportions for Normal, Heavyweight, and Mass Concrete
- NSR-10 Título C — Concreto Estructural (C.4 Durabilidad, C.5 Proporciones)
- ACI 318-19 — Building Code Requirements for Structural Concrete

## Autor

Comando Construcciones SAS — Bogotá, Colombia
