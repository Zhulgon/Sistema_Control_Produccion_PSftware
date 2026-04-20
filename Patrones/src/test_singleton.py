"""
Prueba conceptual del patrón Singleton para el caso MES.

Ejecución:
python test_singleton.py
"""

from _bootstrap import ensure_src_path

ensure_src_path()

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
