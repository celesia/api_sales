# API de ventas — Kiosco La Esquina

API en Python que genera datos de ventas ficticios de una cadena de kioscos en Uruguay, para usar como fuente de datos de un proyecto de ingeniería de datos (bootcamp Databricks/Spark). Devuelve una tabla plana (una fila por producto por ticket), pensada para desarmarla en un modelo dimensional aparte.

## Cómo funciona

No hay base de datos. Cada respuesta se calcula en el momento, a partir de una semilla que sale exclusivamente de la fecha pedida. Pedir el mismo día mil veces da exactamente el mismo resultado, siempre, en cualquier instancia del servidor. No queda ningún rastro guardado en ningún lado.

- **Negocio ficticio:** "Kiosco La Esquina", 5 sucursales en distintos departamentos de Uruguay (Montevideo, Salto, Maldonado, Paysandú, Rivera).
- **Apertura:** 1 de septiembre de 2026. No hay datos antes de esa fecha, ni de fechas futuras.
- **Volumen:** 100 a 150 filas por día de semana, 150 a 200 el fin de semana.
- **Catálogo:** 16 productos en 5 categorías, con precio de lista que sube cada 12 a 25 días (simula inflación). 9 empleados, algunos con traslado real de sucursal.
- **Suciedad deliberada:** nombres mal formateados, precios con coma decimal, campos nulos, cantidades inválidas — para practicar limpieza de datos.
- **Outliers:** por separado de la suciedad de formato, un puñado de filas con valores estadísticamente atípicos (cantidad o precio muy fuera de rango), para practicar detección por percentil.

## Endpoint

```
GET /ventas?fecha=YYYY-MM-DD
GET /ventas?desde=YYYY-MM-DD&hasta=YYYY-MM-DD    (rango, máximo 31 días)
```

Respuesta:

```json
{
  "meta": {"desde": "2026-09-01", "hasta": "2026-09-26", "filas": 3610},
  "data": [
    {
      "ticket_id": "2026-09-10-0001",
      "fecha_hora": "2026-09-10T17:09:00",
      "sucursal_nombre": "Kiosco La Esquina Puerto",
      "sucursal_ciudad": "Paysandú",
      "sucursal_departamento": "Paysandú",
      "vendedor_id": 8,
      "vendedor_nombre": "Agustín Bentancur",
      "producto_id": 12,
      "producto_nombre": "Cigarrillos Nevada",
      "categoria": "Cigarrillos",
      "precio_lista": 260.0,
      "precio_unitario": 260.0,
      "cantidad": 3,
      "descuento": 0,
      "metodo_pago": "mercado_pago",
      "estado_venta": "aprobada"
    }
  ]
}
```

Errores (siempre 400, salvo fecha con formato inválido que da 422):

| Situación | Mensaje |
|---|---|
| Ni `fecha` ni `desde`/`hasta` | Falta 'fecha', o el par 'desde' y 'hasta' |
| `fecha` junto con `desde`/`hasta` | Pedí 'fecha' o el par 'desde'/'hasta', no las dos cosas juntas |
| `desde` posterior a `hasta` | 'desde' no puede ser posterior a 'hasta' |
| Rango de más de 31 días | El rango no puede superar los 31 días |
| Fecha posterior a hoy | No se pueden pedir fechas futuras |
| Fecha anterior al 2026-09-01 | El negocio no tiene datos antes del 2026-09-01 |

**Nota:** `precio_lista` (lo que costaba el producto ese día en el catálogo) y `precio_unitario` (lo que realmente se cobró en esa venta) son campos distintos a propósito — la diferencia es el descuento. También conviven dos formas de representar "algo salió mal": `cantidad` en 0 o negativa es un error de carga (suciedad, para practicar limpieza), mientras que `estado_venta = "devolucion"` es un hecho de negocio real modelado como una fila nueva, nunca como una corrección de la fila original.

## Correr en local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn main:app --reload
```

Después, `http://127.0.0.1:8000/docs` para probarla desde el navegador.

## Estructura

```
main.py              # FastAPI y el único endpoint /ventas
datos_maestros.py    # sucursales, productos, empleados, métodos de pago
generador.py         # toda la lógica de generación, sin FastAPI adentro
tests/
├── test_generador.py   # determinismo, catálogos, suciedad/outliers
└── test_api.py         # contrato HTTP: parámetros, rangos, errores
```

## Despliegue

Desplegada en Vercel (función Python serverless, sin configuración adicional: `main.py` en la raíz con una instancia `app` es un patrón que Vercel detecta solo). Conectada al repo de GitHub para desplegar automáticamente en cada push a `main`.
