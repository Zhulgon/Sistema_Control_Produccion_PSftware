"""
Ejecuta las pruebas conceptuales de las actividades semanales.

Ejecucion:
python run_tests_conceptuales.py
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    tests = [
        path
        for path in sorted(base_dir.glob("test_*.py"))
        if path.name != "run_tests_conceptuales.py"
    ]

    if not tests:
        raise SystemExit("No se encontraron pruebas conceptuales.")

    all_ok = True
    for test in tests:
        print(f"\n>>> Ejecutando {test.name}")
        result = subprocess.run(
            [sys.executable, str(test)],
            capture_output=True,
            text=True,
            cwd=base_dir,
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        if result.returncode == 0:
            print(f"Resultado: OK en {test.name}")
        else:
            print(f"Resultado: ERROR en {test.name}")
            all_ok = False

    if not all_ok:
        raise SystemExit("\nPruebas conceptuales: hubo errores.")

    print("\nPruebas conceptuales: todos los patrones ejecutaron correctamente.")


if __name__ == "__main__":
    main()
