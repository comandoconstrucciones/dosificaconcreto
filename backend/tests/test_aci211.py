"""
Tests del motor ACI 211.1
Casos validados contra ejemplos del Manual ACI 211.1 y NSR-10
"""
import sys, os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calculators.aci211 import diseñar_mezcla, MaterialesInput, calcular_fcr

# ─── Fixture base ────────────────────────────────────────────────────────────

@pytest.fixture
def inp_tipico():
    return MaterialesInput(
        fc_especificado=21.0,
        slump_mm=90,
        tms_mm=19.0,
        ge_ag_ssd=2.65,
        absorcion_ag=1.0,
        humedad_ag=2.0,
        peso_unitario_ag=1580,
        ge_af_ssd=2.60,
        absorcion_af=1.5,
        humedad_af=3.5,
        modulo_finura=2.80,
        tipo_cemento="I",
        clase_exposicion="S0"
    )

# ─── Tests de f'cr ───────────────────────────────────────────────────────────

def test_fcr_sin_historial_fc21():
    fcr, _ = calcular_fcr(21, None, 0)
    assert fcr == pytest.approx(29.5, abs=0.1)

def test_fcr_sin_historial_fc35():
    fcr, _ = calcular_fcr(35, None, 0)
    assert fcr == pytest.approx(43.5, abs=0.1)

def test_fcr_con_historial():
    fcr, metodo = calcular_fcr(21, 3.5, 20)
    assert fcr > 21
    assert "historial" in metodo.lower()

def test_fcr_sin_historial_alta_resistencia():
    """Para f'c > 35 MPa usa fórmula diferente"""
    fcr, _ = calcular_fcr(42, None, 0)
    assert fcr == pytest.approx(51.2, abs=0.5)

# ─── Tests de mezcla típica ──────────────────────────────────────────────────

def test_mezcla_tipica_resultado_valido(inp_tipico):
    r = diseñar_mezcla(inp_tipico)
    assert r.fcr == pytest.approx(29.5, abs=0.5)
    assert 0.50 <= r.wc_diseno <= 0.68
    assert 190 <= r.agua_lab <= 220
    assert 300 <= r.cemento <= 420
    assert r.ag_grueso_ssd > 0
    assert r.ag_fino_ssd > 0

def test_suma_volumenes_es_1m3(inp_tipico):
    """La suma de volúmenes absolutos debe ser 1.000 m³ ± 2%"""
    r = diseñar_mezcla(inp_tipico)
    vol_agua = r.agua_lab / 1000
    vol_cem  = r.cemento / (3.15 * 1000)
    vol_ag   = r.ag_grueso_ssd / (inp_tipico.ge_ag_ssd * 1000)
    vol_af   = r.ag_fino_ssd   / (inp_tipico.ge_af_ssd * 1000)
    vol_aire = r.aire_pct / 100
    total = vol_agua + vol_cem + vol_ag + vol_af + vol_aire
    assert abs(total - 1.0) < 0.02, f"Suma volúmenes = {total:.4f} m³ (esperado ~1.000)"

def test_mezcla_alta_resistencia():
    inp = MaterialesInput(
        fc_especificado=35.0, slump_mm=75, tms_mm=19.0,
        ge_ag_ssd=2.70, absorcion_ag=0.8, humedad_ag=1.0, peso_unitario_ag=1580,
        ge_af_ssd=2.62, absorcion_af=1.8, humedad_af=3.5,
        modulo_finura=2.70, tipo_cemento="I", clase_exposicion="S0"
    )
    r = diseñar_mezcla(inp)
    assert r.wc_diseno <= 0.50
    assert r.cemento >= 380

def test_durabilidad_C2_limita_wc():
    """Clase C2 debe limitar a/c a máximo 0.40"""
    inp = MaterialesInput(
        fc_especificado=35.0, slump_mm=75, tms_mm=19.0,
        ge_ag_ssd=2.70, absorcion_ag=0.8, humedad_ag=1.0, peso_unitario_ag=1580,
        ge_af_ssd=2.62, absorcion_af=1.8, humedad_af=3.5,
        modulo_finura=2.70, tipo_cemento="I", clase_exposicion="C2"
    )
    r = diseñar_mezcla(inp)
    assert r.wc_diseno <= 0.40
    assert r.cemento >= 335

def test_durabilidad_alerta_cuando_fc_bajo():
    """Si f'c es menor al mínimo de la clase de exposición, debe generar alerta"""
    inp = MaterialesInput(
        fc_especificado=21.0, slump_mm=90, tms_mm=19.0,
        ge_ag_ssd=2.65, absorcion_ag=1.0, humedad_ag=2.0, peso_unitario_ag=1580,
        ge_af_ssd=2.60, absorcion_af=1.5, humedad_af=3.5,
        modulo_finura=2.80, tipo_cemento="I", clase_exposicion="C2"
    )
    r = diseñar_mezcla(inp)
    # C2 requiere f'c >= 35 MPa — debe generar alerta
    assert any("C2" in a or "35" in a or "durabilidad" in a.lower() for a in r.alertas)

def test_proporcion_cemento_es_1(inp_tipico):
    r = diseñar_mezcla(inp_tipico)
    assert r.proporcion_cemento == 1.0
    assert r.proporcion_fino > 0
    assert r.proporcion_grueso > 0

def test_correccion_humedad_reduce_agua(inp_tipico):
    """Con agregados húmedos, el agua de campo debe ser menor que la de lab"""
    r = diseñar_mezcla(inp_tipico)
    # Humedad > absorción → agregan agua → menos agua libre a poner
    from calculators.aci211 import corregir_humedad
    ajuste = corregir_humedad(r, inp_tipico, 4.0, 6.0)
    assert ajuste["agua_campo"] < r.agua_lab

def test_agua_campo_negativa_genera_alerta():
    """Agregados muy húmedos pueden dar agua campo negativa — debe generar alerta"""
    inp = MaterialesInput(
        fc_especificado=21, slump_mm=90, tms_mm=19,
        ge_ag_ssd=2.65, absorcion_ag=1.0, humedad_ag=8.0,  # muy húmedo
        peso_unitario_ag=1580,
        ge_af_ssd=2.60, absorcion_af=1.5, humedad_af=10.0,  # muy húmedo
        modulo_finura=2.80, tipo_cemento="I", clase_exposicion="S0"
    )
    r = diseñar_mezcla(inp)
    if r.agua_campo < 0:
        assert any("negativa" in a.lower() or "saturad" in a.lower() for a in r.alertas)
