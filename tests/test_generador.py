"""Tests de las funciones puras del generador: nada de HTTP acá."""

from datetime import date, timedelta

from datos_maestros import APERTURA, EMPLEADOS
from generador import generar_ventas_del_dia, precio_lista, sucursal_asignada


def test_misma_fecha_da_las_mismas_filas():
    a = generar_ventas_del_dia(date(2026, 9, 10))
    b = generar_ventas_del_dia(date(2026, 9, 10))
    assert a == b


def test_fechas_distintas_dan_resultados_distintos():
    a = generar_ventas_del_dia(date(2026, 9, 10))
    b = generar_ventas_del_dia(date(2026, 9, 11))
    assert a != b


def test_volumen_diario_dentro_del_rango_esperado():
    for fecha in [date(2026, 9, 1) + timedelta(days=i) for i in range(14)]:
        filas = generar_ventas_del_dia(fecha)
        techo = 210 if fecha.weekday() >= 5 else 160  # + margen por ticket duplicado y multi-línea
        piso = 90
        assert piso <= len(filas) <= techo, f"{fecha}: {len(filas)} filas"


def test_precio_lista_no_decrece_y_es_estable_dentro_del_intervalo():
    producto = {
        "id": 999, "nombre": "Test", "categoria": "Test",
        "precio_inicial": 100.0, "fecha_alta": APERTURA,
        "intervalo_ajuste_dias": 10, "incremento_pct": 0.05,
    }
    p0 = precio_lista(producto, APERTURA)
    p5 = precio_lista(producto, APERTURA + timedelta(days=5))  # mismo intervalo
    p10 = precio_lista(producto, APERTURA + timedelta(days=10))  # siguiente intervalo
    assert p0 == p5
    assert p10 > p0


def test_sucursal_asignada_respeta_el_traslado():
    lucia = next(e for e in EMPLEADOS if e["nombre"] == "Lucía Ferreira")
    antes = sucursal_asignada(lucia, date(2026, 9, 5))
    despues = sucursal_asignada(lucia, date(2026, 9, 20))
    assert antes["id"] == 1
    assert despues["id"] == 3
    assert antes["id"] != despues["id"]


def test_suciedad_y_outliers_aparecen_pero_estan_acotados():
    filas = []
    for i in range(60):
        filas.extend(generar_ventas_del_dia(APERTURA + timedelta(days=i)))

    n = len(filas)
    con_precio_como_texto = sum(1 for f in filas if isinstance(f["precio_unitario"], str))
    con_vendedor_nulo = sum(1 for f in filas if f["vendedor_id"] is None)
    con_cantidad_extrema = sum(1 for f in filas if f["cantidad"] >= 50)

    # Aparece al menos una vez cada tipo...
    assert con_precio_como_texto > 0
    assert con_vendedor_nulo > 0
    assert con_cantidad_extrema > 0
    # ...pero los outliers son claramente más raros que la suciedad de formato.
    assert con_cantidad_extrema < con_precio_como_texto
    assert con_cantidad_extrema / n < 0.02
