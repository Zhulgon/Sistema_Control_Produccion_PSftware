"""
Practica guiada del proyecto MES funcional.

Ejecucion:
python run_practica_guiada.py
"""

from __future__ import annotations

from pprint import pprint

from mes_functional_app import OrderExecutionRequest, build_default_mes_project


def print_scope() -> None:
    print("\n=== ALCANCE FUNCIONAL REAL ===")
    print("Incluye:")
    print("- Inicio de orden de produccion")
    print("- Despacho de orden a linea por protocolo")
    print("- Integracion con gateway legacy")
    print("- Cierre de orden con reporte final enriquecido")
    print("- Calculo de metricas globales y capacidad de planta")
    print("No incluye:")
    print("- Integracion fisica con maquinaria real")
    print("- Base de datos o interfaz web productiva")


def print_pattern_map(app) -> None:
    print("\n=== MAPA PATRON -> CODIGO ===")
    for item in app.get_pattern_map():
        print(f"[{item.pattern}]")
        print(f"  objetivo: {item.objective}")
        print(f"  modulo: {item.module}")
        print(f"  clases: {item.key_classes}")
        print(f"  uso: {item.usage_point}")


def print_execution_log(result: dict) -> None:
    print("\n=== BITACORA DE EJECUCION ===")
    for i, step in enumerate(result["execution_log"], start=1):
        print(
            f"{i:02d}. {step['step']} | patron={step['pattern']} | "
            f"modulo={step['module']}"
        )


def main() -> None:
    app = build_default_mes_project()

    print_scope()
    print_pattern_map(app)

    request = OrderExecutionRequest(
        template_key="cnc_standard",
        order_id="OP-2026-4001",
        planned_units=650,
        shift="DAY",
        protocol="opcua",
    )
    result = app.execute_order(request)

    print_execution_log(result)

    print("\n=== RESULTADO FINAL ===")
    print(f"status={result['status']} order={result['order_id']}")
    print(f"dispatch={result['dispatch']}")
    print(f"legacy_sync={result['legacy_sync']}")
    print("controller_summary:")
    pprint(result["controller_summary"], sort_dicts=False)
    print("final_report:")
    pprint(result["final_report"], sort_dicts=False)


if __name__ == "__main__":
    main()
