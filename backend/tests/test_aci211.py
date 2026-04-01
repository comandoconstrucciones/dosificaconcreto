"""
Tests del motor ACI 211.1
Casos validados contra ejemplos del Manual ACI 211.1 y NSR-10
"""
import pytest
from calculators.aci211 import diseñar_mezcla, MaterialesInput, calcular_fcr


class TestFcrSinHistorial:
    """Verificar f'cr sin historial — Tabla ACI 318-19"""

    @pytest.mark.parametrize("fc,fcr_esperado", [
        (17, 24.0),
        (21, 29.5),
        (28, 36.5),
        (35, 43.5),
        (42, 51.2),
    ])
    def test_fcr_tabla(self, fc, fcr_esperado):
        fcr, metodo = calcular_fcr(fc, None, 0)
        assert abs(fcr - fcr_esperado) < 2.0, f"f'c={fc}: f'cr={fcr:.1f}, esperado ~{fcr_esperado}"
        assert "Sin historial" in metodo

    def test_fcr_con_historial(self):
        """f'cr con historial estadístico (s=4.0 MPa, n=30)"""
        fcr, metodo = calcular_fcr(21, 4.0, 30)
        assert fcr > 21, "f'cr debe ser mayor que f'c"
        assert "Con historial" in metodo

    def test_fcr_historial_insuficiente(self):
        """Con n<15 debe usar tabla sin historial"""
        fcr, metodo = calcular_fcr(21, 4.0, 10)
        assert "Sin historial" in metodo


class TestEjemploTipicoColombia:
    """Caso típico: f'c=21 MPa, slump 75-100mm, TMS 19mm"""

    @pytest.fixture
    def resultado(self):
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
        return diseñar_mezcla(inp)

    def test_fcr_rango(self, resultado):
        assert 28 <= resultado.fcr <= 32, f"f'cr fuera de rango: {resultado.fcr}"

    def test_wc_rango(self, resultado):
        assert 0.50 <= resultado.wc_diseno <= 0.68, f"a/c fuera de rango: {resultado.wc_diseno}"

    def test_agua_rango(self, resultado):
        assert 190 <= resultado.agua_lab <= 215, f"Agua fuera de rango: {resultado.agua_lab}"

    def test_cemento_rango(self, resultado):
        assert 300 <= resultado.cemento <= 380, f"Cemento fuera de rango: {resultado.cemento}"

    def test_af_positivo(self, resultado):
        assert resultado.ag_fino_ssd > 0, "AF negativo"

    def test_proporciones(self, resultado):
        assert resultado.proporcion_fino > 0
        assert resultado.proporcion_grueso > 0


class TestAltaResistencia:
    """f'c=35 MPa — alta resistencia, clase exposición C2"""

    @pytest.fixture
    def resultado(self):
        inp = MaterialesInput(
            fc_especificado=35.0,
            slump_mm=75,
            tms_mm=19.0,
            ge_ag_ssd=2.70,
            absorcion_ag=0.8,
            humedad_ag=1.0,
            peso_unitario_ag=1580,
            ge_af_ssd=2.62,
            absorcion_af=1.8,
            humedad_af=3.5,
            modulo_finura=2.70,
            tipo_cemento="I",
            clase_exposicion="C2"
        )
        return diseñar_mezcla(inp)

    def test_wc_durabilidad(self, resultado):
        assert resultado.wc_diseno <= 0.40, f"C2 requiere a/c ≤ 0.40, got {resultado.wc_diseno}"

    def test_cemento_minimo(self, resultado):
        assert resultado.cemento >= 335, f"C2 requiere cemento ≥ 335 kg/m³, got {resultado.cemento}"

    def test_cumple_durabilidad(self, resultado):
        assert resultado.cumple_durabilidad


class TestSlumpAlto:
    """f'c=21 MPa, TMS 12.5mm, slump alto — edificio residencial típico"""

    @pytest.fixture
    def resultado(self):
        inp = MaterialesInput(
            fc_especificado=21.0,
            slump_mm=150,
            tms_mm=12.5,
            ge_ag_ssd=2.65,
            absorcion_ag=1.2,
            humedad_ag=0.8,
            peso_unitario_ag=1540,
            ge_af_ssd=2.58,
            absorcion_af=2.0,
            humedad_af=5.0,
            modulo_finura=2.60,
            tipo_cemento="I",
            clase_exposicion="S0"
        )
        return diseñar_mezcla(inp)

    def test_af_positivo(self, resultado):
        assert resultado.ag_fino_ssd > 0

    def test_agua_mayor(self, resultado):
        """Slump alto → más agua que caso típico"""
        assert resultado.agua_lab > 205


class TestSumaVolumenes:
    """Verificar que la suma de volúmenes = 1.0 m³"""

    def test_volumenes_suman_uno(self):
        inp = MaterialesInput(
            fc_especificado=28.0,
            slump_mm=90,
            tms_mm=19.0,
            ge_ag_ssd=2.65,
            absorcion_ag=1.0,
            humedad_ag=1.5,
            peso_unitario_ag=1580,
            ge_af_ssd=2.60,
            absorcion_af=1.5,
            humedad_af=3.0,
            modulo_finura=2.80,
            tipo_cemento="I",
            ge_cemento=3.15,
            clase_exposicion="S0"
        )
        r = diseñar_mezcla(inp)

        vol_agua = r.agua_lab / 1000
        vol_cem = r.cemento / (3.15 * 1000)
        vol_ag = r.ag_grueso_ssd / (inp.ge_ag_ssd * 1000)
        vol_af = r.ag_fino_ssd / (inp.ge_af_ssd * 1000)
        vol_aire = r.aire_pct / 100
        total = vol_agua + vol_cem + vol_ag + vol_af + vol_aire

        assert abs(total - 1.0) < 0.02, f"Suma de volúmenes = {total:.4f} — error > 2%"


class TestCorreccionHumedad:
    """Tests de corrección de humedad en campo"""

    @pytest.fixture
    def resultado_e_input(self):
        inp = MaterialesInput(
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
        from calculators.aci211 import corregir_humedad
        r = diseñar_mezcla(inp)
        return r, inp

    def test_correccion_basica(self, resultado_e_input):
        from calculators.aci211 import corregir_humedad
        r, inp = resultado_e_input
        ajuste = corregir_humedad(r, inp, 3.0, 5.0)
        assert "agua_campo" in ajuste
        assert "ag_grueso_campo" in ajuste
        assert "ag_fino_campo" in ajuste

    def test_humedad_mayor_mas_agua_agregado(self, resultado_e_input):
        """Más humedad → menos agua de amasado necesaria"""
        from calculators.aci211 import corregir_humedad
        r, inp = resultado_e_input
        ajuste_baja = corregir_humedad(r, inp, 1.0, 1.5)
        ajuste_alta = corregir_humedad(r, inp, 5.0, 8.0)
        assert ajuste_alta["agua_campo"] < ajuste_baja["agua_campo"]


class TestClasesExposicion:
    """Verificar todas las clases de exposición NSR-10"""

    @pytest.mark.parametrize("clase,wc_max_esperado", [
        ("S0", None),
        ("S1", 0.50),
        ("S2", 0.45),
        ("C0", None),
        ("C1", 0.50),
        ("C2", 0.40),
        ("F0", None),
        ("F1", 0.45),
        ("F2", 0.40),
        ("W0", None),
        ("W1", 0.50),
        ("W2", 0.45),
    ])
    def test_wc_por_clase(self, clase, wc_max_esperado):
        inp = MaterialesInput(
            fc_especificado=35.0,
            slump_mm=90,
            tms_mm=19.0,
            clase_exposicion=clase,
        )
        r = diseñar_mezcla(inp)
        if wc_max_esperado is not None:
            assert r.wc_diseno <= wc_max_esperado + 0.001, \
                f"Clase {clase}: a/c={r.wc_diseno} > máx={wc_max_esperado}"
