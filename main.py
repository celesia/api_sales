"""API de ventas — Kiosco La Esquina.

Genera datos de ventas ficticios de una cadena de kioscos en Uruguay, de
forma determinista por fecha. No hay base de datos: cada respuesta se
calcula en el momento y no queda ningún rastro en el servidor. Pedir la
misma fecha dos veces siempre da exactamente las mismas filas.

Endpoint único:
    GET /ventas?fecha=YYYY-MM-DD
    GET /ventas?desde=YYYY-MM-DD&hasta=YYYY-MM-DD   (rango, máximo 31 días)

El negocio "abrió" el 2026-09-01: no hay datos antes de esa fecha, ni
después de hoy — no existen ventas del futuro.
"""

from datetime import date, timedelta

from fastapi import FastAPI, HTTPException

from datos_maestros import APERTURA
from generador import generar_ventas_del_dia

app = FastAPI(title="API de ventas — Kiosco La Esquina")

TOPE_DIAS = 31


def _hoy() -> date:
    """Envuelto en una función aparte para que los tests puedan simular
    'más adelante en el tiempo' con monkeypatch, sin depender del reloj
    real de la máquina que corre los tests."""
    return date.today()


@app.get("/")
def raiz():
    return {"mensaje": "API de ventas de Kiosco La Esquina. Ver /docs o GET /ventas."}


@app.get("/ventas")
def ventas(fecha: date | None = None, desde: date | None = None, hasta: date | None = None):
    hoy = _hoy()

    if fecha and (desde or hasta):
        raise HTTPException(400, "Pedí 'fecha' o el par 'desde'/'hasta', no las dos cosas juntas")
    if fecha:
        desde = hasta = fecha
    if not desde or not hasta:
        raise HTTPException(400, "Falta 'fecha', o el par 'desde' y 'hasta'")
    if desde > hasta:
        raise HTTPException(400, "'desde' no puede ser posterior a 'hasta'")
    if (hasta - desde).days + 1 > TOPE_DIAS:
        raise HTTPException(400, f"El rango no puede superar los {TOPE_DIAS} días")
    if hasta > hoy:
        raise HTTPException(400, "No se pueden pedir fechas futuras")
    if desde < APERTURA:
        raise HTTPException(400, f"El negocio no tiene datos antes del {APERTURA.isoformat()}")

    filas: list[dict] = []
    dia = desde
    while dia <= hasta:
        filas.extend(generar_ventas_del_dia(dia))
        dia += timedelta(days=1)

    return {
        "meta": {"desde": str(desde), "hasta": str(hasta), "filas": len(filas)},
        "data": filas,
    }
