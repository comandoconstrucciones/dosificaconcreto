"""
Motor de Análisis Granulométrico
Referencia: ASTM C33 / NTC 174 — Agregados para concreto
Autor: Leonardo Ríos — DosificaConcreto
"""

from dataclasses import dataclass, field
from typing import Optional


# ─── TAMICES ESTÁNDAR ────────────────────────────────────────────────────────

TAMICES_FINO = [
    {"nombre": '9.5mm (3/8")',  "abertura": 9.500, "en_mf": False},
    {"nombre": "4.75mm (#4)",   "abertura": 4.750, "en_mf": True},
    {"nombre": "2.36mm (#8)",   "abertura": 2.360, "en_mf": True},
    {"nombre": "1.18mm (#16)",  "abertura": 1.180, "en_mf": True},
    {"nombre": "0.60mm (#30)",  "abertura": 0.600, "en_mf": True},
    {"nombre": "0.30mm (#50)",  "abertura": 0.300, "en_mf": True},
    {"nombre": "0.15mm (#100)", "abertura": 0.150, "en_mf": True},
    {"nombre": "Fondo",         "abertura": 0.000, "en_mf": False},
]

TAMICES_GRUESO = [
    {"nombre": '37.5mm (1.5")', "abertura": 37.500},
    {"nombre": '25.0mm (1")',   "abertura": 25.000},
    {"nombre": '19.0mm (3/4")', "abertura": 19.000},
    {"nombre": '12.5mm (1/2")', "abertura": 12.500},
    {"nombre": '9.5mm (3/8")',  "abertura": 9.500},
    {"nombre": "4.75mm (#4)",   "abertura": 4.750},
    {"nombre": "2.36mm (#8)",   "abertura": 2.360},
    {"nombre": "Fondo",         "abertura": 0.000},
]

# Tamices unificados para curva combinada (orden descendente por abertura)
TAMICES_COMBINADOS = [
    {"nombre": '37.5mm (1.5")', "abertura": 37.500},
    {"nombre": '25.0mm (1")',   "abertura": 25.000},
    {"nombre": '19.0mm (3/4")', "abertura": 19.000},
    {"nombre": '12.5mm (1/2")', "abertura": 12.500},
    {"nombre": '9.5mm (3/8")',  "abertura": 9.500},
    {"nombre": "4.75mm (#4)",   "abertura": 4.750},
    {"nombre": "2.36mm (#8)",   "abertura": 2.360},
    {"nombre": "1.18mm (#16)",  "abertura": 1.180},
    {"nombre": "0.60mm (#30)",  "abertura": 0.600},
    {"nombre": "0.30mm (#50)",  "abertura": 0.300},
    {"nombre": "0.15mm (#100)", "abertura": 0.150},
]

# ─── LÍMITES ASTM C33 — AGREGADO FINO ───────────────────────────────────────
# % que pasa (mínimo, máximo) por tamiz

LIMITES_FINO_PASA = {
    9.500: (100, 100),
    4.750: (95,  100),
    2.360: (80,  100),
    1.180: (50,   85),
    0.600: (25,   60),
    0.300: (10,   30),
    0.150: (2,    10),
    0.000: (0,     0),
}

# ─── LÍMITES ASTM C33 — AGREGADO GRUESO (% que pasa) ────────────────────────
# Por TMS: {abertura_tamiz: (min_pasa, max_pasa)}

LIMITES_GRUESO = {
    9.5: {   # TMS 3/8" — Tamaño #89
        12.500: (100, 100),
        9.500:  (90,  100),
        4.750:  (20,   55),
        2.360:  (0,    10),
        0.000:  (0,     0),
    },
    12.5: {  # TMS 1/2" — Tamaño #67
        19.000: (100, 100),
        12.500: (90,  100),
        9.500:  (40,   70),
        4.750:  (0,    15),
        2.360:  (0,     5),
        0.000:  (0,     0),
    },
    19.0: {  # TMS 3/4" — Tamaño #57
        25.000: (100, 100),
        19.000: (90,  100),
        12.500: (25,   60),
        9.500:  (0,    30),
        4.750:  (0,    10),
        2.360:  (0,     5),
        0.000:  (0,     0),
    },
    25.0: {  # TMS 1" — Tamaño #467
        37.500: (100, 100),
        25.000: (90,  100),
        19.000: (35,   70),
        12.500: (0,    15),
        9.500:  (0,    15),
        4.750:  (0,     5),
        0.000:  (0,     0),
    },
    37.5: {  # TMS 1.5" — Tamaño #357
        50.000: (100, 100),
        37.500: (90,  100),
        25.000: (35,   70),
        19.000: (0,    15),
        12.500: (0,    15),
        4.750:  (0,     5),
        0.000:  (0,     0),
    },
    50.0: {  # TMS 2" — Tamaño #4
        75.000: (100, 100),
        50.000: (90,  100),
        37.500: (35,   70),
        25.000: (0,    30),
        19.000: (0,    15),
        4.750:  (0,     5),
        0.000:  (0,     0),
    },
    75.0: {  # TMS 3" — Tamaño #3
        100.000: (100, 100),
        75.000:  (90,  100),
        50.000:  (35,   70),
        37.500:  (0,    30),
        25.000:  (0,    15),
        4.750:   (0,     5),
        0.000:   (0,     0),
    },
}

# ─── ZONA ÓPTIMA — Combinada fino + grueso (ICONTEC / NTC 174) ─────────────
# Zona II (ideal): % que pasa de la mezcla combinada
# Referencia: curva Fuller/Thompson para gradación óptima continua
# Estos límites son para TMS 19mm (3/4"), el más común en Colombia

ZONA_OPTIMA_COMBINADA = {
    # abertura_mm: (min_pasa, max_pasa) para mezcla combinada ideal
    37.500: (100, 100),
    25.000: (100, 100),
    19.000: (95,  100),
    12.500: (70,   90),
    9.500:  (55,   80),
    4.750:  (35,   60),
    2.360:  (25,   45),
    1.180:  (17,   35),
    0.600:  (10,   25),
    0.300:  (5,    15),
    0.150:  (2,     8),
}


# ─── DATACLASSES ─────────────────────────────────────────────────────────────

@dataclass
class TamizResultado:
    nombre: str
    abertura_mm: float
    retenido_pct: float
    retenido_acum_pct: float
    pasa_pct: float
    limite_inf: Optional[float]  # % pasa mínimo ASTM C33
    limite_sup: Optional[float]  # % pasa máximo ASTM C33
    cumple: Optional[bool]


@dataclass
class ResultadoGranulometria:
    tipo: str                          # "fino" o "grueso"
    tms_mm: Optional[float]
    modulo_finura: Optional[float]     # Solo para fino
    cumple_astm: bool
    tamices: list[TamizResultado]
    alertas: list[str] = field(default_factory=list)


@dataclass
class TamizCombinado:
    nombre: str
    abertura_mm: float
    pasa_fino_pct: float           # % pasa del fino
    pasa_grueso_pct: float         # % pasa del grueso
    pasa_combinado_pct: float      # % pasa combinado
    zona_inf: Optional[float]     # Zona óptima mín
    zona_sup: Optional[float]     # Zona óptima máx
    en_zona: Optional[bool]


@dataclass
class ResultadoCombinado:
    pct_fino: float                    # % de fino en la mezcla (0-100)
    pct_grueso: float                  # % de grueso en la mezcla (0-100)
    pct_fino_optimo: float             # % fino óptimo calculado
    en_zona_optima: bool
    tamices: list[TamizCombinado]
    alertas: list[str] = field(default_factory=list)


# ─── MOTOR ───────────────────────────────────────────────────────────────────

def calcular_granulometria_fino(retenidos_pct: list[float]) -> ResultadoGranulometria:
    """
    Calcula granulometría de agregado fino.
    retenidos_pct: lista de 8 valores [%ret 3/8", #4, #8, #16, #30, #50, #100, fondo]
    """
    tamices_def = TAMICES_FINO
    assert len(retenidos_pct) == len(tamices_def), \
        f"Se esperan {len(tamices_def)} valores, se recibieron {len(retenidos_pct)}"

    alertas = []

    # Calcular acumulados y % pasa
    acum = 0.0
    tamices = []
    suma_mf = 0.0

    for i, (tam, ret) in enumerate(zip(tamices_def, retenidos_pct)):
        acum += ret
        pasa = max(0.0, 100.0 - acum)
        abertura = tam["abertura"]

        # Límites
        lims = LIMITES_FINO_PASA.get(abertura)
        lim_inf = lims[0] if lims else None
        lim_sup = lims[1] if lims else None

        if lim_inf is not None:
            cumple = lim_inf <= pasa <= lim_sup
        else:
            cumple = None

        # Módulo de finura: suma de %ret acumulados en tamices con en_mf=True
        if tam["en_mf"]:
            suma_mf += acum

        tamices.append(TamizResultado(
            nombre=tam["nombre"],
            abertura_mm=abertura,
            retenido_pct=round(ret, 1),
            retenido_acum_pct=round(acum, 1),
            pasa_pct=round(pasa, 1),
            limite_inf=lim_inf,
            limite_sup=lim_sup,
            cumple=cumple,
        ))

    modulo_finura = round(suma_mf / 100, 2)
    cumple_total = all(t.cumple for t in tamices if t.cumple is not None)

    if not 2.3 <= modulo_finura <= 3.1:
        alertas.append(
            f"Módulo de finura {modulo_finura} fuera del rango recomendado (2.3 – 3.1)"
        )
    if modulo_finura < 2.3:
        alertas.append("Arena muy fina — puede requerir mayor contenido de cemento")
    if modulo_finura > 3.1:
        alertas.append("Arena gruesa — puede reducir trabajabilidad")

    return ResultadoGranulometria(
        tipo="fino",
        tms_mm=None,
        modulo_finura=modulo_finura,
        cumple_astm=cumple_total,
        tamices=tamices,
        alertas=alertas,
    )


def calcular_granulometria_grueso(retenidos_pct: list[float], tms_mm: float) -> ResultadoGranulometria:
    """
    Calcula granulometría de agregado grueso.
    retenidos_pct: lista de 8 valores para tamices definidos en TAMICES_GRUESO
    tms_mm: 9.5, 12.5, 19, 25, 37.5, 50 o 75
    """
    tamices_def = TAMICES_GRUESO
    assert len(retenidos_pct) == len(tamices_def), \
        f"Se esperan {len(tamices_def)} valores, se recibieron {len(retenidos_pct)}"

    limites = LIMITES_GRUESO.get(tms_mm, LIMITES_GRUESO[19.0])
    alertas = []

    acum = 0.0
    tamices = []

    for tam, ret in zip(tamices_def, retenidos_pct):
        acum += ret
        pasa = max(0.0, 100.0 - acum)
        abertura = tam["abertura"]

        lims = limites.get(abertura)
        lim_inf = lims[0] if lims else None
        lim_sup = lims[1] if lims else None

        if lim_inf is not None:
            cumple = lim_inf <= pasa <= lim_sup
        else:
            cumple = None

        tamices.append(TamizResultado(
            nombre=tam["nombre"],
            abertura_mm=abertura,
            retenido_pct=round(ret, 1),
            retenido_acum_pct=round(acum, 1),
            pasa_pct=round(pasa, 1),
            limite_inf=lim_inf,
            limite_sup=lim_sup,
            cumple=cumple,
        ))

    cumple_total = all(t.cumple for t in tamices if t.cumple is not None)

    return ResultadoGranulometria(
        tipo="grueso",
        tms_mm=tms_mm,
        modulo_finura=None,
        cumple_astm=cumple_total,
        tamices=tamices,
        alertas=alertas,
    )


def _obtener_pasa_por_abertura(resultado: ResultadoGranulometria) -> dict[float, float]:
    """Extrae dict {abertura_mm: pasa_pct} de un resultado de granulometría"""
    return {t.abertura_mm: t.pasa_pct for t in resultado.tamices}


def calcular_combinada(
    resultado_fino: ResultadoGranulometria,
    resultado_grueso: ResultadoGranulometria,
    pct_fino: float,
) -> ResultadoCombinado:
    """
    Calcula curva granulométrica combinada.
    pct_fino: porcentaje de agregado fino en la mezcla (0-100).
    La curva combinada es: pasa_comb = (pct_fino/100)*pasa_fino + (pct_grueso/100)*pasa_grueso
    """
    pct_grueso = 100.0 - pct_fino
    alertas = []

    pasa_fino = _obtener_pasa_por_abertura(resultado_fino)
    pasa_grueso = _obtener_pasa_por_abertura(resultado_grueso)

    tamices = []
    todas_en_zona = True

    for tam in TAMICES_COMBINADOS:
        abertura = tam["abertura"]
        # Para tamices que no existen en fino, pasa=100% (todo pasa)
        pf = pasa_fino.get(abertura, 100.0)
        # Para tamices que no existen en grueso, pasa=0% (nada pasa)
        pg = pasa_grueso.get(abertura, 0.0)

        # Pasa combinado
        pasa_comb = (pct_fino / 100.0) * pf + (pct_grueso / 100.0) * pg

        # Zona óptima
        zona = ZONA_OPTIMA_COMBINADA.get(abertura)
        zona_inf = zona[0] if zona else None
        zona_sup = zona[1] if zona else None

        if zona_inf is not None:
            en_zona = zona_inf <= pasa_comb <= zona_sup
            if not en_zona:
                todas_en_zona = False
        else:
            en_zona = None

        tamices.append(TamizCombinado(
            nombre=tam["nombre"],
            abertura_mm=abertura,
            pasa_fino_pct=round(pf, 1),
            pasa_grueso_pct=round(pg, 1),
            pasa_combinado_pct=round(pasa_comb, 1),
            zona_inf=zona_inf,
            zona_sup=zona_sup,
            en_zona=en_zona,
        ))

    # Calcular % fino óptimo (buscar el % que maximiza puntos dentro de zona)
    mejor_pct = pct_fino
    mejor_score = -1
    for test_pct in range(20, 61):
        score = 0
        for tam in TAMICES_COMBINADOS:
            abertura = tam["abertura"]
            pf = pasa_fino.get(abertura, 100.0)
            pg = pasa_grueso.get(abertura, 0.0)
            pasa_test = (test_pct / 100.0) * pf + ((100 - test_pct) / 100.0) * pg
            zona = ZONA_OPTIMA_COMBINADA.get(abertura)
            if zona and zona[0] <= pasa_test <= zona[1]:
                score += 1
        if score > mejor_score:
            mejor_score = score
            mejor_pct = float(test_pct)

    if not todas_en_zona:
        alertas.append(
            f"La curva combinada ({pct_fino:.0f}% fino / {pct_grueso:.0f}% grueso) "
            f"está fuera de la zona óptima en algunos tamices"
        )
        alertas.append(
            f"Porcentaje de fino óptimo sugerido: {mejor_pct:.0f}%"
        )

    return ResultadoCombinado(
        pct_fino=round(pct_fino, 1),
        pct_grueso=round(pct_grueso, 1),
        pct_fino_optimo=mejor_pct,
        en_zona_optima=todas_en_zona,
        tamices=tamices,
        alertas=alertas,
    )


def get_limites_fino() -> list[dict]:
    """Retorna límites ASTM C33 para fino — listo para graficar"""
    return [
        {"abertura_mm": ab, "limite_inf": lims[0], "limite_sup": lims[1]}
        for ab, lims in LIMITES_FINO_PASA.items()
        if ab > 0
    ]


def get_limites_grueso(tms_mm: float) -> list[dict]:
    """Retorna límites ASTM C33 para grueso según TMS — listo para graficar"""
    limites = LIMITES_GRUESO.get(tms_mm, LIMITES_GRUESO[19.0])
    return [
        {"abertura_mm": ab, "limite_inf": lims[0], "limite_sup": lims[1]}
        for ab, lims in limites.items()
        if ab > 0
    ]


def get_zona_optima() -> list[dict]:
    """Retorna zona óptima combinada — listo para graficar"""
    return [
        {"abertura_mm": ab, "zona_inf": lims[0], "zona_sup": lims[1]}
        for ab, lims in ZONA_OPTIMA_COMBINADA.items()
    ]
