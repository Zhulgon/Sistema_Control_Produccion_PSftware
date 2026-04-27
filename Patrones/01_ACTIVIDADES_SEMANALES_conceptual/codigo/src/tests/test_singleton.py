"""
Prueba conceptual del patrón Singleton para el caso MES.

Ejecución:
python test_singleton.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from singleton_m import MESController


def run_singleton_test():
    a = MESController()
    b = MESController()

    assert a is b

    print("Singleton test conceptual: OK")
    print(f"id(a)={id(a)}")
    print(f"id(b)={id(b)}")


if __name__ == "__main__":
    run_singleton_test()
