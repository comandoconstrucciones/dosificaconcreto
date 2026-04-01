"""
DosificaConcreto API — FastAPI
Endpoints para diseño de mezclas ACI 211.1 y análisis granulométrico ASTM C33
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from calculators.aci211 import (
    diseñar_mezcla, corregir_humedad, MaterialesInput, ResultadoMezcla
)
from calculators.granulometry import (
    calcular_granulometria_fino, calcular_granulometria_grueso,
    calcular_combinada, get_limites_fino, get_limites_grueso,
    get_zona_optima, TAMICES_FINO, TAMICES_GRUESO, TAMICES_COMBINADOS,
)

app = FastAPI(
    title="DosificaConcreto API",
    description="Diseño de mezclas de concreto según ACI 211.1 y NSR-10",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── SCHEMAS ─────────────────────────────────────────────────────────────────

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
    clase_exposicion: str = Field("S0", description="Clase de exposición NSR-10")
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


class CombinedGranulometriaInput(BaseModel):
    retenidos_fino: list[float] = Field(..., description="% retenido fino (8 tamices)")
    retenidos_grueso: list[float] = Field(..., description="% retenido grueso (8 tamices)")
    tms_mm: float = Field(19.0, description="TMS del grueso (mm)")
    pct_fino: float = Field(40.0, description="% de fino en la mezcla", ge=0, le=100)


# ─── ENDPOINTS MEZCLA ────────────────────────────────────────────────────────

@app.post("/api/mezcla/calcular")
def calcular_mezcla(data: MezclaInput):
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
            clase_exposicion=data.clase_exposicion,
            desv_estandar=data.desv_estandar,
            n_muestras=data.n_muestras,
        )
        resultado = diseñar_mezcla(inp)
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en el cálculo: {str(e)}")


@app.post("/api/mezcla/corregir-humedad")
def corregir_humedad_campo(data: CorreccionHumedadInput):
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
            clase_exposicion=data.inp.clase_exposicion,
        )
        from calculators.aci211 import ResultadoMezcla
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
        ajuste = corregir_humedad(
            resultado_obj, inp,
            data.humedad_ag_campo,
            data.humedad_af_campo
        )
        return {"ok": True, "ajuste": ajuste}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en corrección: {str(e)}")


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
        raise HTTPException(status_code=400, detail="tipo debe ser 'fino' o 'grueso'")


@app.post("/api/granulometria/calcular")
def calcular_granulo(data: GranulometriaInput):
    """Analiza curva granulométrica y verifica cumplimiento ASTM C33"""
    try:
        # Validar que la suma de retenidos sea ~100%
        suma = sum(data.retenidos_pct)
        if abs(suma - 100.0) > 1.5:
            raise ValueError(
                f"La suma de % retenidos debe ser 100% (±1.5%). Suma actual: {suma:.1f}%"
            )

        if data.tipo == "fino":
            if len(data.retenidos_pct) != 8:
                raise ValueError("Se requieren 8 valores para agregado fino")
            resultado = calcular_granulometria_fino(data.retenidos_pct)
        elif data.tipo == "grueso":
            if len(data.retenidos_pct) != 8:
                raise ValueError("Se requieren 8 valores para agregado grueso")
            resultado = calcular_granulometria_grueso(data.retenidos_pct, data.tms_mm or 19.0)
        else:
            raise ValueError("tipo debe ser 'fino' o 'grueso'")

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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/api/granulometria/combinada")
def calcular_combinada_endpoint(data: CombinedGranulometriaInput):
    """Calcula curva granulométrica combinada fino + grueso con zona óptima"""
    try:
        # Validar sumas
        suma_fino = sum(data.retenidos_fino)
        if abs(suma_fino - 100.0) > 1.5:
            raise ValueError(f"Suma retenidos fino: {suma_fino:.1f}% (debe ser ~100%)")
        suma_grueso = sum(data.retenidos_grueso)
        if abs(suma_grueso - 100.0) > 1.5:
            raise ValueError(f"Suma retenidos grueso: {suma_grueso:.1f}% (debe ser ~100%)")

        if len(data.retenidos_fino) != 8:
            raise ValueError("Se requieren 8 valores para agregado fino")
        if len(data.retenidos_grueso) != 8:
            raise ValueError("Se requieren 8 valores para agregado grueso")

        r_fino = calcular_granulometria_fino(data.retenidos_fino)
        r_grueso = calcular_granulometria_grueso(data.retenidos_grueso, data.tms_mm)
        r_comb = calcular_combinada(r_fino, r_grueso, data.pct_fino)

        return {
            "ok": True,
            "resultado": {
                "pct_fino": r_comb.pct_fino,
                "pct_grueso": r_comb.pct_grueso,
                "pct_fino_optimo": r_comb.pct_fino_optimo,
                "en_zona_optima": r_comb.en_zona_optima,
                "alertas": r_comb.alertas,
                "fino_cumple_astm": r_fino.cumple_astm,
                "grueso_cumple_astm": r_grueso.cumple_astm,
                "modulo_finura": r_fino.modulo_finura,
                "tamices": [
                    {
                        "nombre": t.nombre,
                        "abertura_mm": t.abertura_mm,
                        "pasa_fino_pct": t.pasa_fino_pct,
                        "pasa_grueso_pct": t.pasa_grueso_pct,
                        "pasa_combinado_pct": t.pasa_combinado_pct,
                        "zona_inf": t.zona_inf,
                        "zona_sup": t.zona_sup,
                        "en_zona": t.en_zona,
                    }
                    for t in r_comb.tamices
                ],
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/api/granulometria/zona-optima")
def zona_optima():
    """Retorna zona óptima combinada para graficar"""
    return {"ok": True, "zona": get_zona_optima()}


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
