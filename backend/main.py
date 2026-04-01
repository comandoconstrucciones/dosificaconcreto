"""
DosificaConcreto API — FastAPI
Endpoints para diseño de mezclas ACI 211.1 y análisis granulométrico ASTM C33
"""

import logging
import os
import sys
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

sys.path.insert(0, os.path.dirname(__file__))
from calculators.aci211 import (
    diseñar_mezcla, corregir_humedad, MaterialesInput, ResultadoMezcla
)
from calculators.granulometry import (
    calcular_granulometria_fino, calcular_granulometria_grueso,
    get_limites_fino, get_limites_grueso,
    TAMICES_FINO, TAMICES_GRUESO
)

# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("dosificaconcreto")

# ─── APP ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DosificaConcreto API",
    description="Diseño de mezclas de concreto según ACI 211.1 y NSR-10",
    version="1.1.0",
)

# ─── RATE LIMITING ───────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS — solo dominios propios ────────────────────────────────────────────
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",") if os.environ.get("ALLOWED_ORIGINS") else [
    "https://dosificaconcreto.com",
    "https://www.dosificaconcreto.com",
    "http://localhost:3000",   # desarrollo local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ─── GZIP — reduce payload ~60% ──────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=500)


# ─── SCHEMAS ─────────────────────────────────────────────────────────────────

class ClaseExposicion(str, Enum):
    """Clases de exposición NSR-10 C.4.2 — valores permitidos"""
    S0 = "S0"; S1 = "S1"; S2 = "S2"; S3 = "S3"
    C0 = "C0"; C1 = "C1"; C2 = "C2"
    F0 = "F0"; F1 = "F1"; F2 = "F2"
    W0 = "W0"; W1 = "W1"; W2 = "W2"


class MezclaInput(BaseModel):
    fc_especificado: float = Field(21.0, description="f'c especificado (MPa)", ge=10, le=70)
    slump_mm: float = Field(90.0, description="Slump objetivo (mm)", ge=25, le=200)
    tms_mm: float = Field(19.0, description="Tamaño máximo nominal (mm)")
    ge_ag_ssd: float = Field(2.65, description="Gravedad específica AG SSD", ge=2.0, le=3.5)
    absorcion_ag: float = Field(1.0, description="Absorción AG (%)", ge=0, le=10)
    humedad_ag: float = Field(2.0, description="Humedad superficial AG (%)", ge=0, le=15)
    peso_unitario_ag: float = Field(1580.0, description="Peso unitario AG seco suelto (kg/m³)")
    ge_af_ssd: float = Field(2.60, description="Gravedad específica AF SSD", ge=2.0, le=3.5)
    absorcion_af: float = Field(1.5, description="Absorción AF (%)", ge=0, le=10)
    humedad_af: float = Field(3.5, description="Humedad superficial AF (%)", ge=0, le=20)
    modulo_finura: float = Field(2.80, description="Módulo de finura AF", ge=2.0, le=3.5)
    tipo_cemento: str = Field("I", description="Tipo de cemento: I, II, III, IV, V, IP")
    ge_cemento: Optional[float] = Field(None, description="Gravedad específica cemento (opcional)")
    aire_incorporado: bool = Field(False, description="¿Concreto con aire incorporado?")
    contenido_aire_pct: Optional[float] = Field(None, description="Contenido de aire % (si se incorpora)")
    clase_exposicion: ClaseExposicion = Field(ClaseExposicion.S0, description="Clase de exposición NSR-10")
    desv_estandar: Optional[float] = Field(None, description="Desviación estándar histórica (MPa)")
    n_muestras: int = Field(0, description="Número de muestras en historial")


class CorreccionHumedadInput(BaseModel):
    resultado: dict
    inp: MezclaInput
    humedad_ag_campo: float = Field(..., ge=0, le=15)
    humedad_af_campo: float = Field(..., ge=0, le=20)


class GranulometriaInput(BaseModel):
    tipo: str = Field(..., description="'fino' o 'grueso'")
    tms_mm: Optional[float] = Field(19.0, description="TMS para grueso (mm)")
    retenidos_pct: list[float] = Field(..., description="% retenido por tamiz")


# ─── ENDPOINTS MEZCLA ────────────────────────────────────────────────────────

@app.post("/api/mezcla/calcular")
@limiter.limit("30/minute")
def calcular_mezcla(request: Request, data: MezclaInput):
    """Diseño completo de mezcla según ACI 211.1 + verificación NSR-10"""
    try:
        inp = MaterialesInput(
            fc_especificado=data.fc_especificado,
            slump_mm=data.slump_mm,
            tms_mm=data.tms_mm,
            ge_ag_ssd=data.ge_ag_ssd,
            absorcion_ag=data.absorcion_ag,
            humedad_ag=data.humedad_ag,
            peso_unitario_ag=data.peso_unitario_ag,
            ge_af_ssd=data.ge_af_ssd,
            absorcion_af=data.absorcion_af,
            humedad_af=data.humedad_af,
            modulo_finura=data.modulo_finura,
            tipo_cemento=data.tipo_cemento,
            ge_cemento=data.ge_cemento,
            aire_incorporado=data.aire_incorporado,
            contenido_aire_pct=data.contenido_aire_pct,
            clase_exposicion=data.clase_exposicion.value,
            desv_estandar=data.desv_estandar,
            n_muestras=data.n_muestras,
        )
        resultado = diseñar_mezcla(inp)
        logger.info(f"Mezcla calculada: f'c={data.fc_especificado} MPa, fcr={resultado.fcr}")
        return {
            "ok": True,
            "resultado": {
                "fc_especificado": resultado.fc_especificado,
                "fcr": resultado.fcr,
                "wc_resistencia": resultado.wc_resistencia,
                "wc_durabilidad": resultado.wc_durabilidad,
                "wc_diseno": resultado.wc_diseno,
                "agua_lab": resultado.agua_lab,
                "cemento": resultado.cemento,
                "bultos_cemento": round(resultado.cemento / 50, 1),
                "ag_grueso_ssd": resultado.ag_grueso_ssd,
                "ag_fino_ssd": resultado.ag_fino_ssd,
                "aire_pct": resultado.aire_pct,
                "agua_campo": resultado.agua_campo,
                "ag_grueso_campo": resultado.ag_grueso_campo,
                "ag_fino_campo": resultado.ag_fino_campo,
                "proporcion_cemento": 1.0,
                "proporcion_fino": resultado.proporcion_fino,
                "proporcion_grueso": resultado.proporcion_grueso,
                "cumple_resistencia": resultado.cumple_resistencia,
                "cumple_durabilidad": resultado.cumple_durabilidad,
                "alertas": resultado.alertas,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en calcular_mezcla: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al calcular la mezcla. Verifique los datos ingresados.")


@app.post("/api/mezcla/corregir-humedad")
@limiter.limit("60/minute")
def corregir_humedad_campo(request: Request, data: CorreccionHumedadInput):
    """Ajuste rápido de proporciones de campo por cambio de humedad"""
    try:
        inp = MaterialesInput(
            fc_especificado=data.inp.fc_especificado,
            slump_mm=data.inp.slump_mm,
            tms_mm=data.inp.tms_mm,
            ge_ag_ssd=data.inp.ge_ag_ssd,
            absorcion_ag=data.inp.absorcion_ag,
            humedad_ag=data.inp.humedad_ag,
            peso_unitario_ag=data.inp.peso_unitario_ag,
            ge_af_ssd=data.inp.ge_af_ssd,
            absorcion_af=data.inp.absorcion_af,
            humedad_af=data.inp.humedad_af,
            modulo_finura=data.inp.modulo_finura,
            tipo_cemento=data.inp.tipo_cemento,
            clase_exposicion=data.inp.clase_exposicion.value,
        )
        r = data.resultado
        resultado_obj = ResultadoMezcla(
            fc_especificado=r["fc_especificado"],
            fcr=r["fcr"],
            wc_resistencia=r["wc_resistencia"],
            wc_durabilidad=r.get("wc_durabilidad"),
            wc_diseno=r["wc_diseno"],
            agua_lab=r["agua_lab"],
            cemento=r["cemento"],
            ag_grueso_ssd=r["ag_grueso_ssd"],
            ag_fino_ssd=r["ag_fino_ssd"],
            aire_pct=r["aire_pct"],
            agua_campo=r["agua_campo"],
            ag_grueso_campo=r["ag_grueso_campo"],
            ag_fino_campo=r["ag_fino_campo"],
        )
        ajuste = corregir_humedad(resultado_obj, inp, data.humedad_ag_campo, data.humedad_af_campo)
        return {"ok": True, "ajuste": ajuste}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Campo requerido faltante: {e}")
    except Exception as e:
        logger.error(f"Error en corregir_humedad: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al corregir humedad.")


@app.get("/api/mezcla/valores-tipicos")
def valores_tipicos():
    """Valores típicos para Colombia (Bogotá) como punto de partida"""
    return {
        "ok": True,
        "valores": {
            "ge_ag_ssd": 2.65,
            "absorcion_ag": 1.0,
            "humedad_ag": 2.0,
            "peso_unitario_ag": 1580,
            "ge_af_ssd": 2.60,
            "absorcion_af": 1.5,
            "humedad_af": 3.5,
            "modulo_finura": 2.80,
            "ge_cemento_tipo_I": 3.15,
            "nota": "Valores típicos Bogotá D.C. — verificar con ensayos de laboratorio"
        }
    }


# ─── ENDPOINTS GRANULOMETRÍA ─────────────────────────────────────────────────

@app.get("/api/granulometria/limites/{tipo}")
def limites_granulometria(tipo: str, tms: float = 19.0):
    """Límites ASTM C33 para fino o grueso"""
    if tipo == "fino":
        return {"ok": True, "limites": get_limites_fino(), "tamices": TAMICES_FINO}
    elif tipo == "grueso":
        return {"ok": True, "limites": get_limites_grueso(tms), "tamices": TAMICES_GRUESO}
    else:
        raise HTTPException(status_code=400, detail="El tipo debe ser 'fino' o 'grueso'")


@app.post("/api/granulometria/calcular")
@limiter.limit("30/minute")
def calcular_granulo(request: Request, data: GranulometriaInput):
    """Analiza curva granulométrica y verifica cumplimiento ASTM C33"""
    try:
        # Validar suma de retenidos
        suma = sum(data.retenidos_pct)
        if abs(suma - 100.0) > 2.0:
            raise HTTPException(
                status_code=400,
                detail=f"La suma de porcentajes retenidos debe ser 100% ± 2%. Suma actual: {suma:.1f}%"
            )

        if data.tipo == "fino":
            if len(data.retenidos_pct) != 8:
                raise HTTPException(status_code=400, detail="Se requieren exactamente 8 valores para agregado fino")
            resultado = calcular_granulometria_fino(data.retenidos_pct)
        elif data.tipo == "grueso":
            if len(data.retenidos_pct) != 8:
                raise HTTPException(status_code=400, detail="Se requieren exactamente 8 valores para agregado grueso")
            resultado = calcular_granulometria_grueso(data.retenidos_pct, data.tms_mm or 19.0)
        else:
            raise HTTPException(status_code=400, detail="El tipo debe ser 'fino' o 'grueso'")

        logger.info(f"Granulometría calculada: tipo={data.tipo}, cumple={resultado.cumple_astm}, MF={resultado.modulo_finura}")
        return {
            "ok": True,
            "resultado": {
                "tipo": resultado.tipo,
                "tms_mm": resultado.tms_mm,
                "modulo_finura": resultado.modulo_finura,
                "cumple_astm": resultado.cumple_astm,
                "alertas": resultado.alertas,
                "tamices": [
                    {
                        "nombre": t.nombre,
                        "abertura_mm": t.abertura_mm,
                        "retenido_pct": t.retenido_pct,
                        "retenido_acum_pct": t.retenido_acum_pct,
                        "pasa_pct": t.pasa_pct,
                        "limite_inf": t.limite_inf,
                        "limite_sup": t.limite_sup,
                        "cumple": t.cumple,
                    }
                    for t in resultado.tamices
                ]
            }
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en calcular_granulo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al calcular granulometría.")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.1.0"}
