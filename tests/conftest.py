"""Se ejecuta antes de importar cualquier módulo de test. Define la API key
de prueba en el entorno, porque main.py la exige apenas se importa
(API_KEY = os.environ["API_KEY"]) — sin esto, importar main fallaría con
un KeyError antes de poder correr ningún test.
"""

import os

os.environ.setdefault("API_KEY", "clave-de-test")
