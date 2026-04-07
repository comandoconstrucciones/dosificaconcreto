"""
Motor ACI 211.1 — Diseño de Mezclas de Concreto Normal
Referencia: ACI 211.1-91 (Reapproved 2009) + NSR-10 C.4 / C.5
Unidades: kg, m³, MPa
Autor: Leonardo Ríos — DosificaConcreto
"""

from dataclasses import dataclass, field
from typing import Optional
import math


# ─── TABLAS ACI 211.1 ────────────────────────────────────────────────────────

# Tabla 6.3.3 — Contenido aproximado de agua de mezclado (kg/m³)
# Dimensión máxima del agregado (mm): [9.5, 12.5, 19, 25, 37.5, 50, 75]
# Slump: 25-50mm, 75-100mm, 150-175mm
AGUA_SIN_AIRE = {
    "25-50":   [207, 199, 190, 179, 166, 154, 130],
    "75-100":  [228, 216, 205, 193, 181, 169, 145],
    "150-175": [243, 228, 216, 202, 190, 178, 160],
}
AGUA_CON_AIRE = {
    "25-50":   [181, 175, 168, 160, 150, 142, 122],
    "75-100":  [202, 193, 184, 175, 165, 157, 133],
    "150-175": [216, 205, 197, 184, 174, 166, 154],
}
TMS_LIST = [9.5, 12.5, 19.0, 25.0, 37.5, 50.0, 75.0]

# Tabla 6.3.4 — Relación a/c por RESISTENCIA (sin aire)
# f'c (MPa): [15, 20, 25, 30, 35, 40, 45]
FC_LIST    = [15,   20,   25,   30,   35,   40,   45]
WC_RESIST  = [0.80, 0.70, 0.61, 0.54, 0.48, 0.43, 0.38]

# Relación a/c por DURABILIDAD (NSR-10 Tabla C.4.2.1)
# clase_exposicion: (a/c_max, cemento_min kg/m³, fc_min MPa)
DURABILIDAD = {
    # Congelación y deshielo (F)
    "F0": (None,  None, None),
    "F1": (0.45,  335,  31),
    "F2": (0.40,  335,  35),
    # Sulfatos (S)
    "S0": (None,  None, None),
    "S1": (0.50,  335,  28),
    "S2": (0.45,  335,  31),
    "S3": (0.45,  335,  31),  # + cemento especial
    # Baja permeabilidad (W)
    "W0": (None,  None, None),
    "W1": (0.50,  None, 28),
    "W2": (0.45,  None, 31),
    # Corrosión refuerzo (C)
    "C0": (None,  None, None),
    "C1": (0.50,  None, 28),
    "C2": (0.40,  335,  35),
}

# Tabla 6.3.6 — Volumen de agregado grueso seco por m³
# Índice: filas = módulo de finura (2.40, 2.60, 2.80, 3.00)
# Columnas = TMS (9.5, 12.5, 19, 25, 37.5, 50, 75)
MF_LIST  = [2.40, 2.60, 2.80, 3.00]
VOL_AG   = {
    9.5:  [0.50, 0.48, 0.46, 0.44],
    12.5: [0.59, 0.57, 0.55, 0.53],
    19.0: [0.66, 0.64, 0.62, 0.60],
    25.0: [0.71, 0.69, 0.67, 0.65],
    37.5: [0.75, 0.73, 0.71, 0.69],
    50.0: [0.78, 0.76, 0.74, 0.72],
    75.0: [0.82, 0.80, 0.78, 0.76],
}

# Contenido de aire atrapado (%) por TMS
AIRE_ATRAPADO = {
    9.5:  3.0,
    12.5: 2.5,
    19.0: 2.0,
    25.0: 1.5,
    37.5: 1.0,
    50.0: 0.5,
    75.0: 0.3,
}

# Gravedad específica del cemento por tipo
GE_CEMENTO = {
    "I":   3.15,
    "II":  3.15,
    "III": 3.15,
    "IV":  3.20,
    "V":   3.15,
    "IP":  2.90,   # Puzolánico
    "IS":  3.00,   # Con escoria
}


# ─── DATACLASSES ─────────────────────────────────────────────────────────────

@dataclass
class MaterialesInput:
    """Datos de entrada de materiales del laboratorio"""
    # Resistencia y trabajabilidad
    fc_especificado: float          # f'c MPa
    slump_mm: float                 # Slump objetivo mm

    # Agregado grueso
    tms_mm: float                   # Tamaño máx nominal mm (9.5, 12.5, 19, 25, 37.5)
    ge_ag_ssd: float = 2.65         # Gravedad específica SSD
    absorcion_ag: float = 1.5       # Absorción % 
    humedad_ag: float = 0.5         # Humedad superficial % (campo)
    peso_unitario_ag: float = 1550  # kg/m³ (seco suelto)

    # Agregado fino
    ge_af_ssd: float = 2.60         # Gravedad específica SSD
    absorcion_af: float = 2.0       # Absorción %
    humedad_af: float = 1.0         # Humedad superficial % (campo)
    modulo_finura: float = 2.80     # Módulo de finura

    # Cemento
    tipo_cemento: str = "I"         # Tipo: I, II, III, IV, V, IP
    ge_cemento: Optional[float] = None  # Si None, usa tabla

    # Concreto con aire incorporado
    aire_incorporado: bool = False
    contenido_aire_pct: Optional[float] = None  # Si None, usa tabla

    # Exposición (NSR-10)
    clase_exposicion: str = "S0"    # F0-F2, S0-S3, W0-W2, C0-C2

    # Historial de resistencia
    desv_estandar: Optional[float] = None  # MPa — si None usa Tabla 5.3.1.2
    n_muestras: int = 0             # N° muestras para calcular s


@dataclass 
class ResultadoMezcla:
    """Resultado completo del diseño de mezcla ACI 211"""
    # Resistencia requerida
    fc_especificado: float
    fcr: float                      # f'cr requerida MPa
    
    # Relación a/c
    wc_resistencia: float
    wc_durabilidad: Optional[float]
    wc_diseno: float                # El menor de los dos
    
    # Proporciones por m³ (laboratorio)
    agua_lab: float                 # kg
    cemento: float                  # kg
    ag_grueso_ssd: float            # kg
    ag_fino_ssd: float              # kg
    aire_pct: float                 # %
    
    # Proporciones por m³ (campo — corregidas por humedad)
    agua_campo: float               # kg (agua libre a agregar)
    ag_grueso_campo: float          # kg
    ag_fino_campo: float            # kg
    
    # Proporciones en peso (C:AF:AG)
    proporcion_cemento: float = 1.0
    proporcion_fino: float = 0.0
    proporcion_grueso: float = 0.0
    
    # Verificaciones
    cumple_resistencia: bool = True
    cumple_durabilidad: bool = True
    alertas: list = field(default_factory=list)
    
    # Costo estimado (opcional)
    costo_por_m3: Optional[float] = None


# ─── FUNCIONES AUXILIARES ────────────────────────────────────────────────────

def _interpolar(x: float, x_list: list, y_list: list) -> float:
    """Interpolación lineal entre tabla"""
    if x <= x_list[0]:
        return y_list[0]
    if x >= x_list[-1]:
        return y_list[-1]
    for i in range(len(x_list) - 1):
        if x_list[i] <= x <= x_list[i+1]:
            t = (x - x_list[i]) / (x_list[i+1] - x_list[i])
            return y_list[i] + t * (y_list[i+1] - y_list[i])
    return y_list[-1]


def _tms_indice(tms: float) -> int:
    """Retorna índice del TMS más cercano en TMS_LIST"""
    diferencias = [abs(tms - t) for t in TMS_LIST]
    return diferencias.index(min(diferencias))


def _slump_categoria(slump_mm: float) -> str:
    """Clasifica slump en categoría para tabla de agua"""
    if slump_mm <= 62:
        return "25-50"
    elif slump_mm <= 125:
        return "75-100"
    else:
        return "150-175"


def calcular_fcr(fc: float, desv: Optional[float], n: int) -> tuple[float, str]:
    """
    Calcula f'cr (resistencia requerida promedio) según ACI 318 / NSR-10 C.5.3.2
    Retorna (fcr, método_usado)
    """
    if desv is not None and n >= 15:
        # Método con historial — el mayor de:
        fcr1 = fc + 1.34 * desv
        fcr2 = fc + 2.33 * desv - 3.45  # Para f'c <= 35 MPa
        if fc > 35:
            fcr2 = 0.90 * fc + 2.33 * desv
        fcr = max(fcr1, fcr2)
        metodo = f"Con historial (s={desv:.1f} MPa, n={n})"
    else:
        # Sin historial — Tabla 5.3.2.2 ACI 318
        if fc < 21:
            fcr = fc + 7.0
        elif fc <= 35:
            fcr = fc + 8.5
        else:
            fcr = 1.10 * fc + 5.0
        metodo = "Sin historial (Tabla ACI 318-19 T.5.3.2.2)"
    
    return fcr, metodo


def calcular_wc_por_resistencia(fcr: float) -> float:
    """Interpolación en Tabla 6.3.4 ACI 211.1 — a/c por resistencia"""
    return _interpolar(fcr, FC_LIST, WC_RESIST)


def calcular_agua(tms: float, slump_mm: float, aire_incorp: bool) -> float:
    """Contenido de agua de mezclado kg/m³ — Tabla 6.3.3 ACI 211.1"""
    cat = _slump_categoria(slump_mm)
    tabla = AGUA_CON_AIRE if aire_incorp else AGUA_SIN_AIRE
    idx = _tms_indice(tms)
    return tabla[cat][idx]


def calcular_vol_ag(tms: float, mf: float) -> float:
    """Volumen de agregado grueso seco por m³ — Tabla 6.3.6"""
    vols_por_mf = VOL_AG.get(tms, VOL_AG[19.0])
    return _interpolar(mf, MF_LIST, vols_por_mf)


# ─── MOTOR PRINCIPAL ─────────────────────────────────────────────────────────

def diseñar_mezcla(inp: MaterialesInput) -> ResultadoMezcla:
    """
    Diseño completo de mezcla ACI 211.1
    Pasos: 1-Fcr, 2-a/c, 3-agua, 4-cemento, 5-AG, 6-AF, 7-corrección humedad
    """
    alertas = []

    # ── Alertas por valores extremos ────────────────────────────────────────
    if inp.fc_especificado > 50:
        alertas.append(
            f"f'c = {inp.fc_especificado} MPa — Concreto de alta resistencia. "
            "Verificar disponibilidad de agregados de calidad y condiciones de curado especiales."
        )
    if inp.slump_mm > 150:
        alertas.append(
            f"Slump = {inp.slump_mm:.0f} mm — Riesgo de segregación y pérdida de resistencia. "
            "Considere usar plastificante en lugar de exceso de agua."
        )
    if inp.modulo_finura < 2.3 or inp.modulo_finura > 3.1:
        alertas.append(
            f"Módulo de finura = {inp.modulo_finura:.2f} está fuera del rango óptimo (2.3 – 3.1). "
            "Puede afectar la trabajabilidad y el contenido de agua."
        )

    # ── Paso 1: Resistencia requerida f'cr ──────────────────────────────────
    fcr, metodo_fcr = calcular_fcr(
        inp.fc_especificado, inp.desv_estandar, inp.n_muestras
    )

    # ── Paso 2: Relación a/c ─────────────────────────────────────────────────
    wc_resist = calcular_wc_por_resistencia(fcr)

    # Verificar durabilidad
    dur = DURABILIDAD.get(inp.clase_exposicion)
    if dur is None:
        alertas.append(
            f"Clase de exposición '{inp.clase_exposicion}' no reconocida — "
            "se omite verificación de durabilidad."
        )
        wc_dur_max = None
        cem_min = None
        fc_dur_min = None
    else:
        wc_dur_max, cem_min, fc_dur_min = dur

    if wc_dur_max is not None:
        wc_diseno = min(wc_resist, wc_dur_max)
        if wc_resist > wc_dur_max:
            alertas.append(
                f"Durabilidad ({inp.clase_exposicion}) limita a/c a {wc_dur_max:.2f} "
                f"(resistencia pedía {wc_resist:.2f})"
            )
    else:
        wc_diseno = wc_resist

    if wc_diseno > 0.80:
        alertas.append(f"a/c = {wc_diseno:.2f} es alto — verifique proporcionalidad")

    # ── Paso 3: Contenido de agua ────────────────────────────────────────────
    agua = calcular_agua(inp.tms_mm, inp.slump_mm, inp.aire_incorporado)

    # Contenido de aire
    if inp.aire_incorporado and inp.contenido_aire_pct is not None:
        aire_pct = inp.contenido_aire_pct
    elif inp.aire_incorporado:
        # Tabla 6.3.3 nota — recomendados
        aire_tabla = {9.5:7.5, 12.5:7.0, 19.0:6.0, 25.0:6.0, 37.5:5.5, 50.0:5.0, 75.0:4.5}
        aire_pct = aire_tabla.get(inp.tms_mm, 6.0)
    else:
        idx = _tms_indice(inp.tms_mm)
        aire_pct = AIRE_ATRAPADO[TMS_LIST[idx]]

    # ── Paso 4: Contenido de cemento ─────────────────────────────────────────
    cemento = agua / wc_diseno

    # Verificar mínimo por durabilidad
    if cem_min is not None and cemento < cem_min:
        cemento = cem_min
        alertas.append(
            f"Cemento aumentado a {cem_min} kg/m³ por requisito de durabilidad "
            f"({inp.clase_exposicion})"
        )
        # Recalcular a/c real
        wc_real = agua / cemento
        alertas.append(f"a/c real ajustado a {wc_real:.3f}")

    # Verificar f'c mínima por durabilidad
    if fc_dur_min is not None and inp.fc_especificado < fc_dur_min:
        alertas.append(
            f"⚠ Clase {inp.clase_exposicion} requiere f'c ≥ {fc_dur_min} MPa "
            f"— especificado: {inp.fc_especificado} MPa"
        )

    # ── Paso 5: Volumen de agregado grueso ───────────────────────────────────
    ge_cem = inp.ge_cemento or GE_CEMENTO.get(inp.tipo_cemento, 3.15)

    vol_ag_frac = calcular_vol_ag(inp.tms_mm, inp.modulo_finura)
    vol_ag_m3   = vol_ag_frac  # m³ de AG seco por m³ de concreto
    masa_ag_ssd = vol_ag_m3 * inp.peso_unitario_ag * (1 + inp.absorcion_ag / 100)

    # ── Paso 6: Volumen absoluto → Agregado fino ─────────────────────────────
    vol_agua  = agua / 1000                          # m³
    vol_cem   = cemento / (ge_cem * 1000)            # m³
    vol_ag    = masa_ag_ssd / (inp.ge_ag_ssd * 1000) # m³
    vol_aire  = aire_pct / 100                       # m³

    vol_af = 1.0 - vol_agua - vol_cem - vol_ag - vol_aire

    if vol_af <= 0:
        raise ValueError(
            f"Volumen de agregado fino resulta negativo ({vol_af:.4f} m³). "
            "Revise la gravedad específica del agregado grueso, el TMS o el peso unitario."
        )

    masa_af_ssd = vol_af * inp.ge_af_ssd * 1000     # kg

    # ── Paso 7: Corrección por humedad (campo) ────────────────────────────────
    # Humedad libre = humedad superficial - absorción
    hum_libre_ag = (inp.humedad_ag - inp.absorcion_ag) / 100
    hum_libre_af = (inp.humedad_af - inp.absorcion_af) / 100

    ag_campo = masa_ag_ssd * (1 + hum_libre_ag)
    af_campo = masa_af_ssd * (1 + hum_libre_af)

    # Agua que aportan los agregados (positivo = aportan, negativo = absorben)
    agua_ag = masa_ag_ssd * hum_libre_ag
    agua_af = masa_af_ssd * hum_libre_af
    agua_campo = agua - agua_ag - agua_af

    if agua_campo < 0:
        alertas.append(
            "⚠ Agua de campo negativa — los agregados están saturados y aportarían agua. "
            "Verificar humedades en campo."
        )

    # ── Proporciones relativas ────────────────────────────────────────────────
    if cemento > 0:
        prop_af = round(masa_af_ssd / cemento, 2)
        prop_ag = round(masa_ag_ssd / cemento, 2)
    else:
        prop_af = prop_ag = 0

    # ── Verificación final ───────────────────────────────────────────────────
    cumple_durabilidad = True
    if wc_dur_max is not None and (agua / cemento) > wc_dur_max + 0.001:
        cumple_durabilidad = False

    return ResultadoMezcla(
        fc_especificado = inp.fc_especificado,
        fcr             = round(fcr, 1),
        wc_resistencia  = round(wc_resist, 3),
        wc_durabilidad  = round(wc_dur_max, 3) if wc_dur_max else None,
        wc_diseno       = round(wc_diseno, 3),
        agua_lab        = round(agua, 1),
        cemento         = round(cemento, 1),
        ag_grueso_ssd   = round(masa_ag_ssd, 1),
        ag_fino_ssd     = round(masa_af_ssd, 1),
        aire_pct        = round(aire_pct, 1),
        agua_campo      = round(agua_campo, 1),
        ag_grueso_campo = round(ag_campo, 1),
        ag_fino_campo   = round(af_campo, 1),
        proporcion_cemento = 1.0,
        proporcion_fino    = prop_af,
        proporcion_grueso  = prop_ag,
        cumple_resistencia = True,
        cumple_durabilidad = cumple_durabilidad,
        alertas            = alertas,
    )


def corregir_humedad(resultado: ResultadoMezcla, inp: MaterialesInput,
                     humedad_ag_campo: float, humedad_af_campo: float) -> dict:
    """
    Recalcula proporciones de campo con nuevas humedades.
    Útil para ajuste día a día en obra.
    """
    hum_libre_ag = (humedad_ag_campo - inp.absorcion_ag) / 100
    hum_libre_af = (humedad_af_campo - inp.absorcion_af) / 100

    ag_campo = resultado.ag_grueso_ssd * (1 + hum_libre_ag)
    af_campo = resultado.ag_fino_ssd   * (1 + hum_libre_af)
    agua_ag  = resultado.ag_grueso_ssd * hum_libre_ag
    agua_af  = resultado.ag_fino_ssd   * hum_libre_af
    agua_campo = resultado.agua_lab - agua_ag - agua_af

    return {
        "agua_campo":      round(agua_campo, 1),
        "ag_grueso_campo": round(ag_campo, 1),
        "ag_fino_campo":   round(af_campo, 1),
        "humedad_ag":      humedad_ag_campo,
        "humedad_af":      humedad_af_campo,
    }
