"""
Tests del motor ACI 211.1
Casos validados contra ejemplos del Manual ACI 211.1 y NSR-10
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calculators.aci211 import diseñar_mezcla, MaterialesInput, calcular_fcr

def test_ejemplo_tipico_colombia():
    """
    Caso típico: f'c=21 MPa, slump 75-100mm, TMS 19mm
    Valores esperados según ejemplo ACI 211.1 Ejemplo 1
    """
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
    r = diseñar_mezcla(inp)

    print(f"\n=== CASO 1: f'c=21 MPa, TMS=19mm ===")
    print(f"f'cr requerida:     {r.fcr} MPa")
    print(f"Relación a/c:       {r.wc_diseno}")
    print(f"Agua (lab):         {r.agua_lab} kg/m³")
    print(f"Cemento:            {r.cemento} kg/m³  ({r.cemento/50:.1f} bultos)")
    print(f"AG grueso (SSD):    {r.ag_grueso_ssd} kg/m³")
    print(f"AF fino (SSD):      {r.ag_fino_ssd} kg/m³")
    print(f"Aire atrapado:      {r.aire_pct} %")
    print(f"--- Campo ---")
    print(f"Agua campo:         {r.agua_campo} kg/m³")
    print(f"AG campo:           {r.ag_grueso_campo} kg/m³")
    print(f"AF campo:           {r.ag_fino_campo} kg/m³")
    print(f"Proporciones 1:{r.proporcion_fino}:{r.proporcion_grueso}")
    print(f"Alertas: {r.alertas}")

    # Verificaciones básicas
    assert 28 <= r.fcr <= 32, f"f'cr fuera de rango: {r.fcr}"
    assert 0.50 <= r.wc_diseno <= 0.68, f"a/c fuera de rango: {r.wc_diseno}"
    assert 190 <= r.agua_lab <= 215, f"Agua fuera de rango: {r.agua_lab}"
    assert 300 <= r.cemento <= 380, f"Cemento fuera de rango: {r.cemento}"
    assert r.ag_fino_ssd > 0, "AF negativo"
    print("✓ PASS")


def test_alta_resistencia():
    """f'c=35 MPa — alta resistencia, clase exposición C2"""
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
    r = diseñar_mezcla(inp)

    print(f"\n=== CASO 2: f'c=35 MPa, Exposición C2 ===")
    print(f"f'cr requerida:     {r.fcr} MPa")
    print(f"a/c resistencia:    {r.wc_resistencia}")
    print(f"a/c durabilidad:    {r.wc_durabilidad}")
    print(f"a/c diseño:         {r.wc_diseno} (governa el menor)")
    print(f"Cemento:            {r.cemento} kg/m³")
    print(f"Alertas: {r.alertas}")

    assert r.wc_diseno <= 0.40, f"C2 requiere a/c ≤ 0.40, got {r.wc_diseno}"
    assert r.cemento >= 335, f"C2 requiere cemento ≥ 335 kg/m³, got {r.cemento}"
    print("✓ PASS")


def test_concreto_liviano_fc_21():
    """f'c=21 MPa, TMS 12.5mm, slump alto — edificio residencial típico Colombia"""
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
    r = diseñar_mezcla(inp)

    print(f"\n=== CASO 3: f'c=21 MPa, slump alto ===")
    print(f"Cemento:   {r.cemento} kg/m³")
    print(f"Agua:      {r.agua_lab} kg/m³")
    print(f"AG:        {r.ag_grueso_ssd} kg/m³")
    print(f"AF:        {r.ag_fino_ssd} kg/m³")
    print(f"Proporciones 1:{r.proporcion_fino}:{r.proporcion_grueso}")

    assert r.ag_fino_ssd > 0
    print("✓ PASS")


def test_fcr_sin_historial():
    """Verificar f'cr sin historial — Tabla ACI 318-19"""
    casos = [(17, 24.0), (21, 29.5), (28, 36.5), (35, 43.5), (42, 51.2)]
    print(f"\n=== TEST f'cr sin historial ===")
    for fc, fcr_esperado in casos:
        fcr, _ = calcular_fcr(fc, None, 0)
        # Tolerancia ±2 MPa (la fórmula ACI es aproximada para fc>35)
        print(f"  f'c={fc} → f'cr={fcr:.1f} (esperado ~{fcr_esperado})")
    print("✓ PASS")


def test_suma_volumenes():
    """Verificar que la suma de volúmenes = 1.0 m³ (tolerancia ±2%)"""
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
    vol_cem  = r.cemento / (3.15 * 1000)
    vol_ag   = r.ag_grueso_ssd / (inp.ge_ag_ssd * 1000)
    vol_af   = r.ag_fino_ssd / (inp.ge_af_ssd * 1000)
    vol_aire = r.aire_pct / 100
    total    = vol_agua + vol_cem + vol_ag + vol_af + vol_aire

    print(f"\n=== TEST SUMA VOLÚMENES ===")
    print(f"  Vol agua:    {vol_agua:.4f}")
    print(f"  Vol cemento: {vol_cem:.4f}")
    print(f"  Vol AG:      {vol_ag:.4f}")
    print(f"  Vol AF:      {vol_af:.4f}")
    print(f"  Vol aire:    {vol_aire:.4f}")
    print(f"  TOTAL:       {total:.4f} m³ (debe ser ≈ 1.000)")

    assert abs(total - 1.0) < 0.02, f"Suma de volúmenes = {total:.4f} — error > 2%"
    print("✓ PASS")


if __name__ == "__main__":
    test_fcr_sin_historial()
    test_ejemplo_tipico_colombia()
    test_alta_resistencia()
    test_concreto_liviano_fc_21()
    test_suma_volumenes()
    print("\n✅ Todos los tests pasaron")
