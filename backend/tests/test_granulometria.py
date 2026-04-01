"""
Tests del motor de análisis granulométrico
Referencia: ASTM C33 / NTC 174
"""
import pytest
from calculators.granulometry import (
    calcular_granulometria_fino,
    calcular_granulometria_grueso,
    get_limites_fino,
    get_limites_grueso,
)


class TestGranulometriaFino:
    """Tests de granulometría de agregado fino"""

    def test_caso_tipico_cumple(self):
        """Arena típica colombiana que cumple ASTM C33"""
        retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
        r = calcular_granulometria_fino(retenidos)

        assert r.tipo == "fino"
        assert r.tms_mm is None
        assert r.modulo_finura is not None
        assert r.cumple_astm is True
        assert len(r.tamices) == 8

    def test_modulo_finura_rango(self):
        """MF de arena típica debe estar entre 2.3 y 3.1"""
        retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
        r = calcular_granulometria_fino(retenidos)
        assert 2.3 <= r.modulo_finura <= 3.1

    def test_suma_pasa_y_retenido(self):
        """% pasa + % retenido acumulado = 100% en cada tamiz"""
        retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
        r = calcular_granulometria_fino(retenidos)
        for t in r.tamices:
            assert abs(t.pasa_pct + t.retenido_acum_pct - 100.0) < 0.2

    def test_pasa_decreciente(self):
        """% que pasa debe ser decreciente (o igual) tamiz a tamiz"""
        retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
        r = calcular_granulometria_fino(retenidos)
        for i in range(len(r.tamices) - 1):
            assert r.tamices[i].pasa_pct >= r.tamices[i + 1].pasa_pct

    def test_arena_muy_fina_alerta(self):
        """Arena muy fina (MF < 2.3) debe generar alerta"""
        # Mucho material fino
        retenidos = [0, 0, 2, 5, 10, 20, 40, 23]
        r = calcular_granulometria_fino(retenidos)
        assert r.modulo_finura < 2.3
        assert any("fina" in a.lower() for a in r.alertas)

    def test_arena_gruesa_alerta(self):
        """Arena gruesa (MF > 3.1) debe generar alerta"""
        # Mucho material grueso
        retenidos = [5, 20, 25, 20, 15, 10, 4, 1]
        r = calcular_granulometria_fino(retenidos)
        assert r.modulo_finura > 3.1
        assert any("gruesa" in a.lower() for a in r.alertas)

    def test_tamices_incorrectos_falla(self):
        """Enviar cantidad incorrecta de tamices debe fallar"""
        with pytest.raises(AssertionError):
            calcular_granulometria_fino([10, 20, 30])

    def test_todos_tamices_tienen_limites(self):
        """Cada tamiz fino debe tener límites ASTM C33"""
        retenidos = [0, 2, 8, 15, 25, 25, 20, 5]
        r = calcular_granulometria_fino(retenidos)
        for t in r.tamices:
            assert t.limite_inf is not None
            assert t.limite_sup is not None

    def test_no_cumple_astm(self):
        """Distribución fuera de límites no debe cumplir"""
        # Todo retenido en un solo tamiz
        retenidos = [0, 95, 0, 0, 0, 0, 0, 5]
        r = calcular_granulometria_fino(retenidos)
        assert r.cumple_astm is False


class TestGranulometriaGrueso:
    """Tests de granulometría de agregado grueso"""

    def test_caso_tipico_tms_19(self):
        """Grava típica TMS 19mm que cumple ASTM C33"""
        retenidos = [0, 0, 5, 25, 30, 30, 8, 2]
        r = calcular_granulometria_grueso(retenidos, 19.0)

        assert r.tipo == "grueso"
        assert r.tms_mm == 19.0
        assert r.modulo_finura is None
        assert len(r.tamices) == 8

    def test_pasa_decreciente_grueso(self):
        """% que pasa debe ser decreciente"""
        retenidos = [0, 0, 5, 25, 30, 30, 8, 2]
        r = calcular_granulometria_grueso(retenidos, 19.0)
        for i in range(len(r.tamices) - 1):
            assert r.tamices[i].pasa_pct >= r.tamices[i + 1].pasa_pct

    @pytest.mark.parametrize("tms", [9.5, 12.5, 19.0, 25.0, 37.5])
    def test_todos_tms_aceptados(self, tms):
        """Cada TMS válido debe poder calcularse sin error"""
        retenidos = [0, 0, 5, 25, 30, 30, 8, 2]
        r = calcular_granulometria_grueso(retenidos, tms)
        assert r.tms_mm == tms
        assert len(r.tamices) == 8

    def test_tamices_incorrectos_falla(self):
        """Enviar cantidad incorrecta de tamices debe fallar"""
        with pytest.raises(AssertionError):
            calcular_granulometria_grueso([10, 20], 19.0)

    def test_no_cumple_grueso(self):
        """Distribución uniforme no cumple ASTM C33"""
        retenidos = [12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5]
        r = calcular_granulometria_grueso(retenidos, 19.0)
        assert r.cumple_astm is False


class TestLimites:
    """Tests de funciones de límites para gráficas"""

    def test_limites_fino_estructura(self):
        limites = get_limites_fino()
        assert len(limites) > 0
        for lim in limites:
            assert "abertura_mm" in lim
            assert "limite_inf" in lim
            assert "limite_sup" in lim
            assert lim["limite_inf"] <= lim["limite_sup"]

    def test_limites_grueso_estructura(self):
        limites = get_limites_grueso(19.0)
        assert len(limites) > 0
        for lim in limites:
            assert "abertura_mm" in lim
            assert "limite_inf" in lim
            assert "limite_sup" in lim

    @pytest.mark.parametrize("tms", [9.5, 12.5, 19.0, 25.0, 37.5])
    def test_limites_grueso_por_tms(self, tms):
        limites = get_limites_grueso(tms)
        assert len(limites) > 0

    def test_limites_fino_no_incluye_fondo(self):
        """Los límites para gráfica no deben incluir abertura 0 (fondo)"""
        limites = get_limites_fino()
        for lim in limites:
            assert lim["abertura_mm"] > 0

    def test_limites_grueso_no_incluye_fondo(self):
        limites = get_limites_grueso(19.0)
        for lim in limites:
            assert lim["abertura_mm"] > 0
