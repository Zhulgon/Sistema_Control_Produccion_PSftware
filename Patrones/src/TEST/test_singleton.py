"""
Prueba conceptual del patrón Singleton para el caso MES.

Ejecución:
python test_singleton.py
"""

from singleton_mes_controller import MESController


def run_singleton_test():
    a = MESController()
    b = MESController()

    assert a is b

    print("Singleton test conceptual: OK")
    print(f"id(a)={id(a)}")
    print(f"id(b)={id(b)}")


if __name__ == "__main__":
    run_singleton_test()
