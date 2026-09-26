"""Generador determinista de ventas: toda la lógica de negocio vive acá,
sin nada de FastAPI adentro. Dado el mismo día, siempre devuelve exactamente
las mismas filas — no hay estado ni base de datos en ningún lado.
"""

import hashlib
import random
from datetime import date, datetime, time, timedelta

from datos_maestros import EMPLEADOS, METODOS_PAGO, PRODUCTOS, SUCURSALES


def seed_for_date(fecha: date) -> int:
    """Semilla 100% reproducible entre procesos. No usa hash() de Python:
    ese hash varía entre procesos según PYTHONHASHSEED, y en un entorno
    serverless cada invocación puede correr en un proceso distinto — eso
    rompería el determinismo entre llamadas."""
    digest = hashlib.sha256(fecha.isoformat().encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def precio_lista(producto: dict, fecha: date) -> float:
    """Función pura de (producto, fecha), sin random: el mismo producto en
    la misma fecha da siempre el mismo precio, sin importar cuántas veces
    ni desde qué instancia serverless se calcule."""
    dias = max((fecha - producto["fecha_alta"]).days, 0)
    n_ajustes = dias // producto["intervalo_ajuste_dias"]
    precio = producto["precio_inicial"] * ((1 + producto["incremento_pct"]) ** n_ajustes)
    return round(precio, 2)


def sucursal_asignada(empleado: dict, fecha: date) -> dict:
    """Función pura de (empleado, fecha): recorre el historial hardcodeado
    y devuelve la sucursal vigente en esa fecha."""
    for periodo in empleado["historial_sucursales"]:
        if periodo["desde"] <= fecha and (periodo["hasta"] is None or fecha <= periodo["hasta"]):
            return next(s for s in SUCURSALES if s["id"] == periodo["sucursal_id"])
    # Fallback defensivo por si se pide una fecha anterior al primer período
    # registrado (no debería pasar, la API ya valida la apertura del negocio).
    primer_periodo = empleado["historial_sucursales"][0]
    return next(s for s in SUCURSALES if s["id"] == primer_periodo["sucursal_id"])


def generar_ventas_del_dia(fecha: date) -> list[dict]:
    rng = random.Random(seed_for_date(fecha))
    es_finde = fecha.weekday() >= 5  # sábado=5, domingo=6
    objetivo = rng.randint(150, 200) if es_finde else rng.randint(100, 150)

    filas: list[dict] = []
    ticket_seq = 1

    while len(filas) < objetivo:
        ticket_id = f"{fecha.isoformat()}-{ticket_seq:04d}"
        n_lineas = rng.choice([1, 1, 1, 2, 2, 3])
        empleado = rng.choice(EMPLEADOS)
        sucursal = sucursal_asignada(empleado, fecha)
        metodo_pago = rng.choice(METODOS_PAGO)
        # Se decide una vez por ticket y la fila queda así para siempre: una
        # "devolucion" es un hecho nuevo con su propio ticket_id más
        # adelante, nunca se corrige la venta original (la fact es inmutable).
        estado_venta = rng.choices(["aprobada", "anulada", "devolucion"], weights=[92, 4, 4])[0]
        fecha_hora = datetime.combine(fecha, time(rng.randint(9, 20), rng.randint(0, 59)))

        for _ in range(n_lineas):
            producto = rng.choice(PRODUCTOS)
            precio = precio_lista(producto, fecha)
            descuento = rng.choice([0, 0, 0, 0.05, 0.1])
            fila = {
                "ticket_id": ticket_id,
                "fecha_hora": fecha_hora.isoformat(),
                "sucursal_nombre": sucursal["nombre"],
                "sucursal_ciudad": sucursal["ciudad"],
                "sucursal_departamento": sucursal["departamento"],
                "vendedor_id": empleado["id"],
                "vendedor_nombre": empleado["nombre"],
                "producto_id": producto["id"],
                "producto_nombre": producto["nombre"],
                "categoria": producto["categoria"],
                "precio_lista": precio,
                "precio_unitario": round(precio * (1 - descuento), 2),
                "cantidad": rng.randint(1, 3),
                "descuento": descuento,
                "metodo_pago": metodo_pago,
                "estado_venta": estado_venta,
            }
            _ensuciar(fila, rng)
            filas.append(fila)

        ticket_seq += 1

    # Ticket duplicado exacto, con probabilidad baja, una vez por día —
    # simula un reintento de ingesta, para practicar deduplicación con
    # ROW_NUMBER en el pipeline downstream.
    if rng.random() < 0.3:
        filas.append(dict(rng.choice(filas)))

    return filas


def _ensuciar(fila: dict, rng: random.Random) -> None:
    """Ensucia la fila in-place, con probabilidades bajas, todo con el mismo
    rng del día (sigue siendo determinista). Primero suciedad de formato
    (más frecuente), después outliers estadísticos (mucho menos frecuentes
    y separados a propósito: se detectan por percentil, no por regex)."""
    if rng.random() < 0.05:
        fila["sucursal_nombre"] = fila["sucursal_nombre"].upper() + "  "
    if rng.random() < 0.03:
        fila["precio_unitario"] = str(fila["precio_unitario"]).replace(".", ",")
    if rng.random() < 0.02:
        fila["vendedor_id"] = None
        fila["vendedor_nombre"] = None
    if rng.random() < 0.02:
        fila["metodo_pago"] = None
    if rng.random() < 0.02 and fila["estado_venta"] == "aprobada":
        fila["cantidad"] = rng.choice([0, -1])
    if rng.random() < 0.04:
        fila["descuento"] = fila["descuento"] * 100  # 0.10 mal cargado como 10

    # Outliers: no son errores de tipeo, son valores estadísticamente
    # atípicos a propósito, con probabilidad mucho más baja que la
    # suciedad de arriba.
    if rng.random() < 0.003:
        fila["cantidad"] = rng.randint(50, 100)
    if rng.random() < 0.003 and isinstance(fila["precio_unitario"], (int, float)):
        # El isinstance evita apilar este outlier sobre una fila que ya
        # quedó con precio_unitario como string por la suciedad de arriba
        # (coma decimal) — cada fila sucia representa un solo problema a
        # la vez, no una combinación de varios.
        fila["precio_unitario"] = round(fila["precio_unitario"] * rng.randint(8, 12), 2)
