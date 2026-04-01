# DosificaConcreto — Roadmap

## v1.0 — MVP ✅ (actual)

**Motor de cálculo ACI 211.1 completo**
- f'cr con y sin historial estadístico (ACI 318-19 Tabla 5.3.2.2)
- Relación a/c por resistencia (interpolación Tabla 6.3.4 ACI 211.1)
- Relación a/c por durabilidad NSR-10 C.4.2 (toma el menor)
- Contenido de agua (Tabla 6.3.3: slump + TMS + aire)
- Volumen absoluto → agregado fino
- Corrección por humedad en campo (laboratorio vs obra)
- Verificación clases de exposición: S0-S3, C0-C2, F0-F2, W0-W2

**API FastAPI**
- POST /api/mezcla/calcular
- POST /api/mezcla/corregir-humedad
- GET /api/mezcla/valores-tipicos
- GET /api/granulometria/limites/{tipo}
- POST /api/granulometria/calcular

**Frontend Next.js 14**
- Diseñador de mezcla con formulario completo
- Sliders de humedad con recálculo en tiempo real
- Página de granulometría con gráfica ASTM C33
- UI mobile-first (para ingenieros en obra)

---

## v1.1 — Granulometría avanzada

- [ ] Curva granulométrica combinada (fino + grueso) para mezcla
- [ ] Verificación zona óptima combinada (Zona II ICONTEC)
- [ ] Cálculo porcentaje de combinación fino/grueso
- [ ] Exportar curva como imagen PNG

---

## v1.2 — Reportes y Costo

- [ ] Exportar memoria de cálculo completa en PDF
  - Encabezado con logo del laboratorio / empresa
  - Todos los pasos del método ACI 211.1
  - Tabla de materiales con unidades
  - Firma e.resp. con número de tarjeta profesional
- [ ] Estimador de costo por m³
  - Precios editables: cemento, arena, gravilla, agua, aditivos
  - Comparador: costo lab vs campo
  - Costo por resistencia (costo/MPa)

---

## v2.0 — Colombia-specific

- [ ] Precios de cemento por ciudad
  - Argos, Cemex, Holcim — Bogotá, Medellín, Cali, Barranquilla
  - Actualización mensual automática
- [ ] Aditivos
  - Plastificantes (reducción agua 10-15%)
  - Superplastificantes (reducción 25-35%)
  - Retardantes y acelerantes
  - Microsílice y ceniza volante (cementos puzolánicos)
- [ ] Concreto bombeado
  - Verificación viscosidad (slump ≥ 150mm)
  - Ajuste por pérdida de slump en línea
- [ ] Corrección por altitud (Bogotá 2600m)
  - Reducción de resistencia por menor presión barométrica
  - Ajuste de contenido de aire atrapado
- [ ] Integración Struos.AI API
  - Consulta automática NSR-10 C.4/C.5 para clase de exposición
  - Referencias normativas en los resultados

---

## v3.0 — SaaS

- [ ] Cuenta de usuario (Google/email)
- [ ] Historial de mezclas guardadas
  - Versionado por proyecto
  - Comparador de mezclas
- [ ] Reportes PDF personalizados
  - Logo del laboratorio
  - Encabezado con datos del proyecto
  - QR de verificación
- [ ] API pública documentada
  - Integración con LIMS de laboratorios
  - Webhooks para actualización de resultados
- [ ] Plan gratuito + plan pro ($X/mes)

---

## Métricas de éxito

| Métrica | v1.0 | v2.0 | v3.0 |
|---------|------|------|------|
| Usuarios únicos/mes | 500 | 5,000 | 20,000 |
| Mezclas calculadas/mes | 1,000 | 15,000 | 80,000 |
| Costo infraestructura | $0 | $50/mes | $200/mes |
| Ingresos | $0 | $0 | $2,000/mes |

## Usuarios objetivo

| Segmento | Tamaño estimado Colombia | Problema que resuelve |
|---|---|---|
| Laboratoristas de concreto | ~3,000 | Herramienta rápida y correcta vs Excel manual |
| Ingenieros residentes | ~15,000 | Ajuste de mezcla en campo sin ir al lab |
| Contratistas medianos | ~5,000 | Verificar mezcla del proveedor |
| Estudiantes ingeniería civil | ~20,000/año | Aprender ACI 211 con herramienta real |
| Supervisores técnicos | ~2,000 | Verificar memoria de cálculo del contratista |
