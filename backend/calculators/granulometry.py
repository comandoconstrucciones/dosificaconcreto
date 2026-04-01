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
    tms_mm: 9.5, 12.5, 19, 25 o 37.5
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
