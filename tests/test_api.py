"""Tests del contrato HTTP del endpoint /ventas."""

import os
from datetime import date, timedelta

from fastapi.testclient import TestClient

import main
from main import APERTURA, TOPE_DIAS, app

client = TestClient(app)
HEADERS = {"X-API-Key": os.environ["API_KEY"]}


def test_sin_api_key_da_401():
    r = client.get("/ventas", params={"fecha": "2026-09-10"})
    assert r.status_code == 401


def test_api_key_incorrecta_da_401():
    r = client.get("/ventas", params={"fecha": "2026-09-10"}, headers={"X-API-Key": "clave-trucha"})
    assert r.status_code == 401


def test_un_dia_suelto_da_lo_mismo_que_dentro_de_un_rango():
    solo = client.get("/ventas", params={"fecha": "2026-09-10"}, headers=HEADERS).json()["data"]
    rango = client.get(
        "/ventas", params={"desde": "2026-09-08", "hasta": "2026-09-12"}, headers=HEADERS
    ).json()["data"]
    del_mismo_dia = [f for f in rango if f["fecha_hora"].startswith("2026-09-10")]
    assert solo == del_mismo_dia


def test_sin_parametros_da_400():
    r = client.get("/ventas", headers=HEADERS)
    assert r.status_code == 400


def test_fecha_junto_con_rango_da_400():
    r = client.get(
        "/ventas",
        params={"fecha": "2026-09-10", "desde": "2026-09-01", "hasta": "2026-09-05"},
        headers=HEADERS,
    )
    assert r.status_code == 400


def test_rango_invertido_da_400():
    r = client.get("/ventas", params={"desde": "2026-09-10", "hasta": "2026-09-01"}, headers=HEADERS)
    assert r.status_code == 400


def test_rango_de_mas_de_31_dias_da_400(monkeypatch):
    # Con la apertura tan reciente, hoy no existe ningún rango real de más
    # de 31 días sin chocar también con el límite de "fecha futura" — para
    # probar el límite de rango de forma aislada, se simula estar más
    # adelante en el tiempo con monkeypatch sobre _hoy().
    monkeypatch.setattr(main, "_hoy", lambda: APERTURA + timedelta(days=90))
    hasta = APERTURA + timedelta(days=TOPE_DIAS)  # 32 días de rango
    r = client.get("/ventas", params={"desde": str(APERTURA), "hasta": str(hasta)}, headers=HEADERS)
    assert r.status_code == 400


def test_rango_de_exactamente_31_dias_da_200(monkeypatch):
    monkeypatch.setattr(main, "_hoy", lambda: APERTURA + timedelta(days=90))
    hasta = APERTURA + timedelta(days=TOPE_DIAS - 1)
    r = client.get("/ventas", params={"desde": str(APERTURA), "hasta": str(hasta)}, headers=HEADERS)
    assert r.status_code == 200


def test_fecha_futura_da_400():
    r = client.get("/ventas", params={"fecha": "2099-01-01"}, headers=HEADERS)
    assert r.status_code == 400


def test_fecha_anterior_a_la_apertura_da_400():
    r = client.get("/ventas", params={"fecha": "2026-08-31"}, headers=HEADERS)
    assert r.status_code == 400


def test_fecha_con_formato_invalido_da_422():
    r = client.get("/ventas", params={"fecha": "31-13-2026"}, headers=HEADERS)
    assert r.status_code == 422


def test_presupuesto_de_bytes_bajo_el_limite_de_vercel():
    # Peor caso teórico: 31 días al volumen máximo posible de fin de semana,
    # con el estimado más generoso de bytes por fila. Vercel corta en 4.5 MB.
    volumen_max_dia = 210  # ver test_volumen_diario_dentro_del_rango_esperado
    bytes_por_fila_estimado = 450
    peor_caso = TOPE_DIAS * volumen_max_dia * bytes_por_fila_estimado
    assert peor_caso < 4_500_000, f"peor caso estimado: {peor_caso} bytes"
