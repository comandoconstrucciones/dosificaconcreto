"""
Tests del motor de análisis granulométrico
Referencia: ASTM C33 / NTC 174
"""
import pytest
from calculators.granulometry import (
    calcular_granulometria_fino,
    calcular_granulometria_grueso,
    calcular_combinada,
    get_limites_fino,
    get_limites_grueso,
    get_zona_optima,
)

# Datos de prueba reutilizables
FINO_TIPICO = [0, 2, 8, 15, 25, 25, 20, 5]
GRUESO_TIPICO = [0, 0, 5, 25, 30, 30, 8, 2]


class TestGranulometriaFino:
    """Tests de granulometría de agregado fino"""

    def test_caso_tipico_cumple(self):
        """Arena típica colombiana que cumple ASTM C33"""
        r = calcular_granulometria_fino(FINO_TIPICO)

        assert r.tipo == "fino"
        assert r.tms_mm is None
        assert r.modulo_finura is not None
        assert r.cumple_astm is True
        assert len(r.tamices) == 8

    def test_modulo_finura_rango(self):
        """MF de arena típica debe estar entre 2.3 y 3.1"""
        r = calcular_granulometria_fino(FINO_TIPICO)
        assert 2.3 <= r.modulo_finura <= 3.1

    def test_suma_pasa_y_retenido(self):
        """% pasa + % retenido acumulado = 100% en cada tamiz"""
        r = calcular_granulometria_fino(FINO_TIPICO)
        for t in r.tamices:
            assert abs(t.pasa_pct + t.retenido_acum_pct - 100.0) < 0.2

    def test_pasa_decreciente(self):
        """% que pasa debe ser decreciente (o igual) tamiz a tamiz"""
        r = calcular_granulometria_fino(FINO_TIPICO)
        for i in range(len(r.tamices) - 1):
            assert r.tamices[i].pasa_pct >= r.tamices[i + 1].pasa_pct

    def test_arena_muy_fina_alerta(self):
        """Arena muy fina (MF < 2.3) debe generar alerta"""
        retenidos = [0, 0, 2, 5, 10, 20, 40, 23]
        r = calcular_granulometria_fino(retenidos)
        assert r.modulo_finura < 2.3
        assert any("fina" in a.lower() for a in r.alertas)

    def test_arena_gruesa_alerta(self):
        """Arena gruesa (MF > 3.1) debe generar alerta"""
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
        r = calcular_granulometria_fino(FINO_TIPICO)
        for t in r.tamices:
            assert t.limite_inf is not None
            assert t.limite_sup is not None

    def test_no_cumple_astm(self):
        """Distribución fuera de límites no debe cumplir"""
        retenidos = [0, 95, 0, 0, 0, 0, 0, 5]
        r = calcular_granulometria_fino(retenidos)
        assert r.cumple_astm is False


class TestGranulometriaGrueso:
    """Tests de granulometría de agregado grueso"""

    def test_caso_tipico_tms_19(self):
        """Grava típica TMS 19mm que cumple ASTM C33"""
        r = calcular_granulometria_grueso(GRUESO_TIPICO, 19.0)

        assert r.tipo == "grueso"
        assert r.tms_mm == 19.0
        assert r.modulo_finura is None
        assert len(r.tamices) == 8

    def test_pasa_decreciente_grueso(self):
        """% que pasa debe ser decreciente"""
        r = calcular_granulometria_grueso(GRUESO_TIPICO, 19.0)
        for i in range(len(r.tamices) - 1):
            assert r.tamices[i].pasa_pct >= r.tamices[i + 1].pasa_pct

    @pytest.mark.parametrize("tms", [9.5, 12.5, 19.0, 25.0, 37.5, 50.0, 75.0])
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


class TestGranulometriaCombinada:
    """Tests de granulometría combinada fino + grueso"""

    @pytest.fixture
    def resultados(self):
        r_fino = calcular_granulometria_fino(FINO_TIPICO)
        r_grueso = calcular_granulometria_grueso(GRUESO_TIPICO, 19.0)
        return r_fino, r_grueso

    def test_combinada_estructura(self, resultados):
        """Resultado combinado tiene la estructura correcta"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 40.0)

        assert r.pct_fino == 40.0
        assert r.pct_grueso == 60.0
        assert len(r.tamices) == 11  # TAMICES_COMBINADOS
        assert r.pct_fino_optimo >= 20 and r.pct_fino_optimo <= 60

    def test_combinada_pasa_entre_fino_y_grueso(self, resultados):
        """% pasa combinado debe estar entre fino y grueso para cada tamiz"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 40.0)

        for t in r.tamices:
            min_pasa = min(t.pasa_fino_pct, t.pasa_grueso_pct)
            max_pasa = max(t.pasa_fino_pct, t.pasa_grueso_pct)
            assert min_pasa - 0.1 <= t.pasa_combinado_pct <= max_pasa + 0.1

    def test_combinada_100_fino(self, resultados):
        """Con 100% fino, combinado = fino"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 100.0)

        for t in r.tamices:
            assert abs(t.pasa_combinado_pct - t.pasa_fino_pct) < 0.2

    def test_combinada_0_fino(self, resultados):
        """Con 0% fino, combinado = grueso"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 0.0)

        for t in r.tamices:
            assert abs(t.pasa_combinado_pct - t.pasa_grueso_pct) < 0.2

    def test_zona_optima_check(self, resultados):
        """Cada tamiz tiene verificación de zona óptima"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 40.0)

        for t in r.tamices:
            if t.zona_inf is not None:
                assert isinstance(t.en_zona, bool)

    def test_pct_fino_optimo_calculado(self, resultados):
        """El % fino óptimo debe estar entre 20 y 60"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 40.0)
        assert 20 <= r.pct_fino_optimo <= 60

    def test_alerta_fuera_zona(self, resultados):
        """Si no está en zona óptima, debe generar alerta"""
        r_fino, r_grueso = resultados
        # Con 10% fino (muy poco), debería estar fuera de zona
        r = calcular_combinada(r_fino, r_grueso, 10.0)
        if not r.en_zona_optima:
            assert len(r.alertas) > 0

    def test_combinada_pasa_decreciente(self, resultados):
        """% pasa combinado debe ser decreciente"""
        r_fino, r_grueso = resultados
        r = calcular_combinada(r_fino, r_grueso, 40.0)
        for i in range(len(r.tamices) - 1):
            assert r.tamices[i].pasa_combinado_pct >= r.tamices[i + 1].pasa_combinado_pct


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

    @pytest.mark.parametrize("tms", [9.5, 12.5, 19.0, 25.0, 37.5, 50.0, 75.0])
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

    def test_zona_optima_estructura(self):
        """Zona óptima tiene estructura correcta"""
        zona = get_zona_optima()
        assert len(zona) > 0
        for z in zona:
            assert "abertura_mm" in z
            assert "zona_inf" in z
            assert "zona_sup" in z
            assert z["zona_inf"] <= z["zona_sup"]
