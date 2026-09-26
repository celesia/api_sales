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

import os
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

from datos_maestros import APERTURA
from generador import generar_ventas_del_dia

app = FastAPI(title="API de ventas — Kiosco La Esquina")

TOPE_DIAS = 31

# La key vive en una variable de entorno (en Vercel: Project Settings ->
# Environment Variables), nunca en el código. Este repo va a estar público
# en GitHub como parte del proyecto del bootcamp, así que la URL de la API
# también va a quedar visible ahí — sin esto, cualquiera podría consumir
# la cuota gratuita de Vercel sin que sirva de nada.
API_KEY = os.environ["API_KEY"]
_api_key_header = APIKeyHeader(name="X-API-Key")


def _verificar_api_key(key: str = Depends(_api_key_header)) -> None:
    # Si falta el header, APIKeyHeader devuelve None acá (no corta antes
    # con 403) — por eso el mismo chequeo cubre tanto "falta" como
    # "vino pero está mal": las dos situaciones dan 401.
    if key != API_KEY:
        raise HTTPException(401, "API key inválida o faltante")


def _hoy() -> date:
    """Envuelto en una función aparte para que los tests puedan simular
    'más adelante en el tiempo' con monkeypatch, sin depender del reloj
    real de la máquina que corre los tests."""
    return date.today()


@app.get("/")
def raiz():
    return {"mensaje": "API de ventas de Kiosco La Esquina. Ver /docs o GET /ventas (requiere API key)."}


@app.get("/ventas", dependencies=[Depends(_verificar_api_key)])
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
