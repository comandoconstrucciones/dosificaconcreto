# DosificaConcreto — Roadmap

## v1.0 — MVP ✅ (actual — completado)

**Motor de cálculo ACI 211.1 completo**
- [x] f'cr con y sin historial estadístico (ACI 318-19 Tabla 5.3.2.2)
- [x] Relación a/c por resistencia (interpolación Tabla 6.3.4 ACI 211.1)
- [x] Relación a/c por durabilidad NSR-10 C.4.2 (toma el menor)
- [x] Contenido de agua (Tabla 6.3.3: slump + TMS + aire)
- [x] Volumen absoluto → agregado fino
- [x] Corrección por humedad en campo (laboratorio vs obra)
- [x] Verificación clases de exposición: S0-S3, C0-C2, F0-F2, W0-W2
- [x] Verificación suma volúmenes = 1.000 m³

**API FastAPI**
- [x] POST /api/mezcla/calcular
- [x] POST /api/mezcla/corregir-humedad
- [x] GET /api/mezcla/valores-tipicos
- [x] GET /api/granulometria/limites/{tipo}
- [x] POST /api/granulometria/calcular
- [x] GET /api/health

**Frontend Next.js 14**
- [x] Diseñador de mezcla con formulario completo (5 secciones)
- [x] Sliders de humedad con recálculo en tiempo real
- [x] Página de granulometría con gráfica ASTM C33 (Recharts)
- [x] UI mobile-first (para ingenieros en obra)
- [x] Home page con tarjetas de módulos
- [x] Header/footer responsive

**Tests**
- [x] 5 test cases: f'cr sin historial, caso típico, alta resistencia, slump alto, volúmenes

---

## v1.0.1 — Deuda técnica y calidad ✅ (completado)

**Infraestructura de desarrollo**
- [x] Crear `requirements.txt` con dependencias Python (fastapi, pydantic, uvicorn, pytest)
- [x] Migrar tests a pytest con `pytest.ini`
- [x] Agregar tests para módulo de granulometría (fino y grueso) — 27 tests nuevos
- [x] Configurar GitHub Actions CI (lint + tests en cada PR)
- [x] Resolver vulnerabilidades npm (`npm audit fix`) — lodash resuelto, next requiere v16
- [x] Agregar `engines` en package.json (Node >= 18)

**Calidad de código**
- [x] Extraer componentes reutilizables a `frontend/src/components/`
  - `Campo.tsx`, `ResultCard.tsx`, `AlertBanner.tsx`, `Badge.tsx`, `ErrorBoundary.tsx`
- [x] Agregar validación backend: `retenidos_pct` debe sumar 100% ± 1.5%
- [x] Mejorar parsing de formulario (`handleChange` con `NUMERIC_FIELDS` set)
- [x] Agregar Error Boundary global en layout

**SEO y accesibilidad**
- [x] Agregar `sitemap.ts` (dinámico) y `robots.txt`
- [x] Open Graph + Twitter Card tags en layout raíz
- [x] Meta description específica por página (mezcla y granulometría layouts)
- [x] Atributos `aria-label` en formularios, selects y sliders
- [x] Path alias `@/*` configurado en tsconfig.json

---

## v1.1 — Granulometría avanzada 📊

- [ ] Curva granulométrica combinada (fino + grueso) para verificar mezcla
- [ ] Verificación zona óptima combinada (Zona II ICONTEC / NTC 174)
- [ ] Cálculo porcentaje óptimo de combinación fino/grueso
- [ ] Exportar curva como imagen PNG (html2canvas o similar)
- [ ] Agregar granulometría de Tamaño #4 (TMS 50mm y 75mm)
- [ ] Tabla de resumen imprimible (CSS @media print)

---

## v1.2 — Reportes y Costo 📄💰

**Memoria de cálculo PDF**
- [ ] Exportar PDF completo del diseño de mezcla (jsPDF o react-pdf)
  - Encabezado con logo del laboratorio / empresa (upload)
  - Todos los pasos del método ACI 211.1 documentados
  - Tabla de materiales con unidades (lab + campo)
  - Tabla de proporciones en peso y volumen
  - Curva granulométrica embebida
  - Firma responsable con número de tarjeta profesional
  - Fecha, proyecto, localización
- [ ] Exportar PDF de análisis granulométrico

**Estimador de costo por m³**
- [ ] Precios editables: cemento (bulto), arena (m³), gravilla (m³), agua, transporte
- [ ] Cálculo costo total por m³ (laboratorio y campo)
- [ ] Comparador costo/resistencia ($/MPa)
- [ ] Desglose: materiales vs mano de obra vs equipo

---

## v1.3 — UX y experiencia móvil 📱

- [ ] PWA (Progressive Web App) — usar offline en obra
- [ ] Modo oscuro (dark mode)
- [ ] Tour/onboarding para usuarios nuevos
- [ ] Tooltips explicativos en cada campo del formulario
- [ ] Tabla de valores típicos de agregados por región de Colombia
- [ ] Botón "Cargar ejemplo" con 3-4 casos predefinidos
- [ ] Guardar último diseño en localStorage
- [ ] Menú hamburguesa móvil en header
- [ ] Compartir resultados por WhatsApp (link con params)

---

## v2.0 — Colombia-specific 🇨🇴

**Precios de cemento por ciudad**
- [ ] Base de datos: Argos, Cemex, Holcim — Bogotá, Medellín, Cali, Barranquilla, Bucaramanga
- [ ] Actualización mensual (manual o scraping)
- [ ] Selector de ciudad en el formulario

**Aditivos**
- [ ] Plastificantes (reducción agua 10-15%)
- [ ] Superplastificantes (reducción 25-35%)
- [ ] Retardantes y acelerantes de fraguado
- [ ] Microsílice y ceniza volante (cementos puzolánicos)
- [ ] Ajuste automático del contenido de agua y a/c con aditivo

**Verificaciones adicionales**
- [ ] Concreto bombeado: verificación viscosidad (slump ≥ 150mm), pérdida de slump en línea
- [ ] Corrección por altitud (Bogotá 2600m, Medellín 1500m)
  - Reducción resistencia por menor presión barométrica
  - Ajuste contenido de aire atrapado
- [ ] Concreto con aire incorporado: tablas de aire recomendado por exposición

**Integración Struos.AI**
- [ ] Consulta automática NSR-10 C.4/C.5 para clase de exposición
- [ ] Referencias normativas enlazadas en resultados

---

## v3.0 — SaaS 🚀

**Cuentas de usuario**
- [ ] Autenticación Google/email (NextAuth o Supabase Auth)
- [ ] Perfil: nombre, empresa, TP (tarjeta profesional), logo

**Historial y proyectos**
- [ ] Guardar mezclas diseñadas por proyecto
- [ ] Versionado de mezclas (v1, v2... por ajustes)
- [ ] Comparador visual de mezclas (tabla lado a lado)
- [ ] Dashboard con métricas: mezclas/mes, materiales más usados

**Reportes PDF personalizados**
- [ ] Logo del laboratorio en encabezado
- [ ] Datos del proyecto (nombre, ubicación, contratista)
- [ ] QR de verificación (link a versión digital)
- [ ] Plantilla editable (colores corporativos)

**API pública documentada**
- [ ] Documentación Swagger/OpenAPI pública
- [ ] API keys para integración con LIMS de laboratorios
- [ ] Webhooks para notificación de resultados
- [ ] SDK JavaScript/Python para integradores

**Monetización**
- [ ] Plan gratuito: 10 mezclas/mes, sin PDF, sin historial
- [ ] Plan Pro ($29.900 COP/mes): ilimitado, PDF, historial, API
- [ ] Plan Empresa ($149.900 COP/mes): multi-usuario, reportes custom, soporte
- [ ] Pasarela de pago: Wompi o MercadoPago (Colombia)

---

## Métricas de éxito

| Métrica | v1.0 | v1.2 | v2.0 | v3.0 |
|---------|------|------|------|------|
| Usuarios únicos/mes | 500 | 2,000 | 5,000 | 20,000 |
| Mezclas calculadas/mes | 1,000 | 6,000 | 15,000 | 80,000 |
| Costo infraestructura | $0 | $0 | $50/mes | $200/mes |
| Ingresos | $0 | $0 | $0 | $2,000 USD/mes |

---

## Usuarios objetivo

| Segmento | Tamaño estimado Colombia | Problema que resuelve |
|---|---|---|
| Laboratoristas de concreto | ~3,000 | Herramienta rápida y correcta vs Excel manual |
| Ingenieros residentes | ~15,000 | Ajuste de mezcla en campo sin ir al lab |
| Contratistas medianos | ~5,000 | Verificar mezcla del proveedor |
| Estudiantes ingeniería civil | ~20,000/año | Aprender ACI 211 con herramienta real |
| Supervisores técnicos | ~2,000 | Verificar memoria de cálculo del contratista |

---

## Prioridad recomendada (próximos pasos)

1. **v1.0.1** — Deuda técnica (CI, tests, requirements.txt) → 1-2 días
2. **v1.2** — PDF de memoria de cálculo → mayor valor percibido por usuarios
3. **v1.3** — PWA + compartir WhatsApp → crecimiento orgánico en Colombia
4. **v1.1** — Granulometría combinada → valor técnico diferenciador
5. **v2.0** — Aditivos + precios → diferenciación competitiva
6. **v3.0** — SaaS con monetización → sostenibilidad del proyecto
