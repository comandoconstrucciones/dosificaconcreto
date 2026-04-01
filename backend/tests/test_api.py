"""
Tests de integración para la API FastAPI
"""
import sys, os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MEZCLA_VALIDA = {
    "fc_especificado": 21,
    "slump_mm": 90,
    "tms_mm": 19,
    "ge_ag_ssd": 2.65,
    "absorcion_ag": 1.0,
    "humedad_ag": 2.0,
    "peso_unitario_ag": 1580,
    "ge_af_ssd": 2.60,
    "absorcion_af": 1.5,
    "humedad_af": 3.5,
    "modulo_finura": 2.80,
    "tipo_cemento": "I",
    "clase_exposicion": "S0",
}

# ─── Health ───────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

# ─── Mezcla ───────────────────────────────────────────────────────────────────

def test_calcular_mezcla_ok():
    r = client.post("/api/mezcla/calcular", json=MEZCLA_VALIDA)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["resultado"]["cemento"] > 0
    assert data["resultado"]["fcr"] == pytest.approx(29.5, abs=0.5)

def test_calcular_mezcla_fc_invalido_bajo():
    """f'c = 5 (menor al mínimo de 10) debe dar 422"""
    payload = {**MEZCLA_VALIDA, "fc_especificado": 5}
    r = client.post("/api/mezcla/calcular", json=payload)
    assert r.status_code == 422

def test_calcular_mezcla_fc_invalido_alto():
    """f'c = 100 (mayor al máximo de 70) debe dar 422"""
    payload = {**MEZCLA_VALIDA, "fc_especificado": 100}
    r = client.post("/api/mezcla/calcular", json=payload)
    assert r.status_code == 422

def test_calcular_mezcla_body_invalido():
    r = client.post("/api/mezcla/calcular", json={"fc_especificado": "no-es-numero"})
    assert r.status_code == 422

def test_valores_tipicos():
    r = client.get("/api/mezcla/valores-tipicos")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "ge_ag_ssd" in data["valores"]

# ─── Granulometría ────────────────────────────────────────────────────────────

def test_granulometria_fino_ok():
    r = client.post("/api/granulometria/calcular", json={
        "tipo": "fino",
        "retenidos_pct": [0, 2, 8, 15, 25, 25, 20, 5]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["resultado"]["modulo_finura"] > 0

def test_granulometria_suma_incorrecta():
    """Suma != 100% debe dar 400"""
    r = client.post("/api/granulometria/calcular", json={
        "tipo": "fino",
        "retenidos_pct": [0, 2, 8, 15, 25, 10, 10, 5]  # suma = 75%
    })
    assert r.status_code == 400
    assert "100%" in r.json()["detail"] or "suma" in r.json()["detail"].lower()

def test_granulometria_tipo_invalido():
    r = client.post("/api/granulometria/calcular", json={
        "tipo": "cemento",
        "retenidos_pct": [0, 2, 8, 15, 25, 25, 20, 5]
    })
    assert r.status_code == 400

def test_limites_fino():
    r = client.get("/api/granulometria/limites/fino")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_limites_grueso():
    r = client.get("/api/granulometria/limites/grueso?tms=19")
    assert r.status_code == 200

def test_limites_tipo_invalido():
    r = client.get("/api/granulometria/limites/otro")
    assert r.status_code == 400
