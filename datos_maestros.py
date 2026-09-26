"""Catálogos maestros del negocio ficticio: constantes de Python, sin base
de datos. `generador.py` los recorre para armar cada venta.
"""

from datetime import date

# Cinco sucursales fijas, en distintos departamentos de Uruguay. Nunca
# cambian (SCD Tipo 1 en el modelo dimensional del pipeline downstream).
SUCURSALES = [
    {"id": 1, "nombre": "Kiosco La Esquina Ciudad Vieja", "ciudad": "Montevideo", "departamento": "Montevideo"},
    {"id": 2, "nombre": "Kiosco La Esquina Centro", "ciudad": "Salto", "departamento": "Salto"},
    {"id": 3, "nombre": "Kiosco La Esquina Playa Mansa", "ciudad": "Maldonado", "departamento": "Maldonado"},
    {"id": 4, "nombre": "Kiosco La Esquina Puerto", "ciudad": "Paysandú", "departamento": "Paysandú"},
    {"id": 5, "nombre": "Kiosco La Esquina Frontera", "ciudad": "Rivera", "departamento": "Rivera"},
]

APERTURA = date(2026, 9, 1)

# intervalo_ajuste_dias es deliberadamente corto (12-25 días, no 30-45):
# con la apertura del negocio en septiembre de 2026, un intervalo largo
# dejaría el proyecto sin ningún cambio de precio real para practicar
# SCD Tipo 2 durante varias semanas. Precios de referencia en pesos
# uruguayos (UYU), ajustables.
PRODUCTOS = [
    {"id": 1, "nombre": "Coca-Cola 500ml", "categoria": "Bebidas", "precio_inicial": 95.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 14, "incremento_pct": 0.04},
    {"id": 2, "nombre": "Agua Salus 500ml", "categoria": "Bebidas", "precio_inicial": 60.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 18, "incremento_pct": 0.03},
    {"id": 3, "nombre": "Jugo Del Valle 300ml", "categoria": "Bebidas", "precio_inicial": 85.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 16, "incremento_pct": 0.03},
    {"id": 4, "nombre": "Cerveza Patricia 473ml", "categoria": "Bebidas", "precio_inicial": 120.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 15, "incremento_pct": 0.04},
    {"id": 5, "nombre": "Alfajor Nikolo", "categoria": "Golosinas", "precio_inicial": 75.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 12, "incremento_pct": 0.04},
    {"id": 6, "nombre": "Alfajor Cachafaz", "categoria": "Golosinas", "precio_inicial": 90.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 13, "incremento_pct": 0.04},
    {"id": 7, "nombre": "Chicle Beldent", "categoria": "Golosinas", "precio_inicial": 35.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 20, "incremento_pct": 0.02},
    {"id": 8, "nombre": "Caramelos Media Hora", "categoria": "Golosinas", "precio_inicial": 40.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 19, "incremento_pct": 0.02},
    {"id": 9, "nombre": "Papas Lays 45g", "categoria": "Snacks", "precio_inicial": 110.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 16, "incremento_pct": 0.03},
    {"id": 10, "nombre": "Doritos 68g", "categoria": "Snacks", "precio_inicial": 130.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 17, "incremento_pct": 0.03},
    {"id": 11, "nombre": "Maní Pehuamar", "categoria": "Snacks", "precio_inicial": 70.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 18, "incremento_pct": 0.03},
    {"id": 12, "nombre": "Cigarrillos Nevada", "categoria": "Cigarrillos", "precio_inicial": 260.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 20, "incremento_pct": 0.05},
    {"id": 13, "nombre": "Cigarrillos Marlboro", "categoria": "Cigarrillos", "precio_inicial": 290.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 20, "incremento_pct": 0.05},
    {"id": 14, "nombre": "Fósforos El Fogón", "categoria": "Almacén", "precio_inicial": 25.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 25, "incremento_pct": 0.02},
    {"id": 15, "nombre": "Pilas Duracell AA x2", "categoria": "Almacén", "precio_inicial": 150.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 22, "incremento_pct": 0.03},
    {"id": 16, "nombre": "Encendedor Bic", "categoria": "Almacén", "precio_inicial": 65.0, "fecha_alta": APERTURA, "intervalo_ajuste_dias": 21, "incremento_pct": 0.03},
]

# 9 empleados. Tres tienen un traslado real de sucursal en la primera
# quincena de apertura, para que la primera carga ya muestre un caso real
# de SCD Tipo 2 en dim_empleado sin tener que esperar semanas.
EMPLEADOS = [
    {"id": 1, "nombre": "Lucía Ferreira", "historial_sucursales": [
        {"sucursal_id": 1, "desde": APERTURA, "hasta": date(2026, 9, 14)},
        {"sucursal_id": 3, "desde": date(2026, 9, 15), "hasta": None},  # se transfirió
    ]},
    {"id": 2, "nombre": "Martín Gómez", "historial_sucursales": [
        {"sucursal_id": 2, "desde": APERTURA, "hasta": None},
    ]},
    {"id": 3, "nombre": "Sofía Rodríguez", "historial_sucursales": [
        {"sucursal_id": 1, "desde": APERTURA, "hasta": None},
    ]},
    {"id": 4, "nombre": "Diego Pereira", "historial_sucursales": [
        {"sucursal_id": 4, "desde": APERTURA, "hasta": date(2026, 9, 10)},
        {"sucursal_id": 5, "desde": date(2026, 9, 11), "hasta": None},  # se transfirió
    ]},
    {"id": 5, "nombre": "Valentina Silva", "historial_sucursales": [
        {"sucursal_id": 3, "desde": APERTURA, "hasta": None},
    ]},
    {"id": 6, "nombre": "Nicolás Acosta", "historial_sucursales": [
        {"sucursal_id": 5, "desde": APERTURA, "hasta": None},
    ]},
    {"id": 7, "nombre": "Camila Torres", "historial_sucursales": [
        {"sucursal_id": 2, "desde": APERTURA, "hasta": date(2026, 9, 12)},
        {"sucursal_id": 1, "desde": date(2026, 9, 13), "hasta": None},  # se transfirió
    ]},
    {"id": 8, "nombre": "Agustín Bentancur", "historial_sucursales": [
        {"sucursal_id": 4, "desde": APERTURA, "hasta": None},
    ]},
    {"id": 9, "nombre": "Florencia Núñez", "historial_sucursales": [
        {"sucursal_id": 1, "desde": APERTURA, "hasta": None},
    ]},
]

METODOS_PAGO = ["efectivo", "tarjeta_debito", "tarjeta_credito", "mercado_pago"]
