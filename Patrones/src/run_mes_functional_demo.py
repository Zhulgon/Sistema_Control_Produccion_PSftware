"""
Demo ejecutable de la fase funcional MES.

Ejecucion:
python run_mes_functional_demo.py
"""

from pprint import pprint

from mes_functional_app import run_demo


def main():
    result = run_demo()
    pprint(result, sort_dicts=False)


if __name__ == "__main__":
    main()
