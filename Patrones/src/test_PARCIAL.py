"""
Ejecuta todas las pruebas conceptuales del parcial semana 6.

Ejecucion:
python test_PARCIAL.py
"""

from pathlib import Path
import subprocess
import sys


# Compatibilidad con nombres antiguos que aun usan algunos tests.
MODULE_ALIASES = {
    "singleton_mes_controller": "singleton_m",
    "factory_machines": "factory_m",
    "abstract_factory_production": "abstract_factory_m",
    "builder_production_report": "builder_m",
}


def ensure_import_compatibility(base_dir: Path) -> list[Path]:
    created_files = []

    for legacy_name, new_name in MODULE_ALIASES.items():
        legacy_path = base_dir / f"{legacy_name}.py"
        new_path = base_dir / f"{new_name}.py"

        if legacy_path.exists() or not new_path.exists():
            continue

        # Shim temporal para no tocar los tests individuales.
        legacy_path.write_text(f"from {new_name} import *\n", encoding="utf-8")
        created_files.append(legacy_path)

    return created_files


def discover_tests(base_dir: Path) -> list[str]:
    tests = []
    for p in sorted(base_dir.glob("test_*.py")):
        if p.name.lower() == "test_parcial.py":
            continue
        tests.append(p.name)
    return tests


def run_test_file(test_file: str) -> bool:
    print(f"\n>>> Ejecutando {test_file}")
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

    return result.returncode == 0


def main():
    base_dir = Path(__file__).resolve().parent
    created_shims = ensure_import_compatibility(base_dir)

    try:
        tests = discover_tests(base_dir)
        if not tests:
            raise SystemExit("No se encontraron tests para ejecutar.")

        all_ok = True
        for test in tests:
            ok = run_test_file(test)
            if not ok:
                all_ok = False
                print(f"Resultado: ERROR en {test}")
            else:
                print(f"Resultado: OK en {test}")

        if not all_ok:
            raise SystemExit("\nParcial tests: hubo errores.")

        print("\nParcial tests: todos los patrones ejecutaron correctamente.")
    finally:
        for shim in created_shims:
            try:
                shim.unlink(missing_ok=True)
            except OSError:
                pass


if __name__ == "__main__":
    main()
