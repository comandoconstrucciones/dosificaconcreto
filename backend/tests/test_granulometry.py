"""
Tests del motor de granulometría ASTM C33
"""
import sys, os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calculators.granulometry import (
    calcular_granulometria_fino, calcular_granulometria_grueso
)

def test_fino_tipico_cumple():
    """Arena típica bogotana que cumple ASTM C33"""
    retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
    r = calcular_granulometria_fino(retenidos)
    assert r.tipo == "fino"
    assert r.cumple_astm is True
    assert 2.3 <= r.modulo_finura <= 3.1

def test_modulo_finura_calculo_correcto():
    """Verificar cálculo numérico del módulo de finura"""
    retenidos = [0, 10, 20, 25, 20, 15, 5, 5]
    r = calcular_granulometria_fino(retenidos)
    # MF = suma %ret.acum. en #4,#8,#16,#30,#50,#100 / 100
    # Acumulados: 10, 30, 55, 75, 90, 95
    mf_esperado = (10 + 30 + 55 + 75 + 90 + 95) / 100
    assert r.modulo_finura == pytest.approx(mf_esperado, abs=0.01)

def test_fino_fuera_limites_no_cumple():
    """Arena con demasiado fino no cumple ASTM C33"""
    # Mucho retenido en tamices pequeños
    retenidos = [0, 0, 2, 5, 10, 20, 40, 23]
    r = calcular_granulometria_fino(retenidos)
    assert r.cumple_astm is False

def test_grueso_tipico_cumple():
    """Gravilla típica TMS 19mm que cumple ASTM C33"""
    retenidos = [0, 0, 5, 25, 30, 30, 8, 2]
    r = calcular_granulometria_grueso(retenidos, tms_mm=19.0)
    assert r.tipo == "grueso"
    assert r.tms_mm == 19.0
    assert r.modulo_finura is None  # Solo para fino

def test_grueso_devuelve_8_tamices():
    retenidos = [0, 0, 5, 25, 30, 30, 8, 2]
    r = calcular_granulometria_grueso(retenidos, tms_mm=19.0)
    assert len(r.tamices) == 8

def test_fino_devuelve_8_tamices():
    retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
    r = calcular_granulometria_fino(retenidos)
    assert len(r.tamices) == 8

def test_suma_incorrecta_no_lanza_excepcion():
    """El motor acepta sumas !=100 — la validación está en el API"""
    retenidos = [0, 2, 8, 15, 25, 25, 10, 5]  # suma = 90
    r = calcular_granulometria_fino(retenidos)
    assert r is not None  # No debe lanzar excepción

def test_pasa_100_en_tamiz_mayor():
    """El tamiz más grande siempre debe tener 100% pasa"""
    retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
    r = calcular_granulometria_fino(retenidos)
    # El primer tamiz (3/8") debe tener 100% pasa
    primer = r.tamices[0]
    assert primer.pasa_pct == pytest.approx(100.0, abs=0.1)
