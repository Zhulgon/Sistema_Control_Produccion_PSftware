"""
Prueba funcional integrada del proyecto MES.

Ejecucion:
python test_mes_functional.py
"""

from mes_functional_app import OrderExecutionRequest, build_default_mes_project


def run_mes_functional_test():
    app = build_default_mes_project()

    result_1 = app.execute_order(
        OrderExecutionRequest(
            template_key="cnc_standard",
            order_id="OP-2026-3001",
            planned_units=500,
            shift="DAY",
            protocol="opcua",
        )
    )

    assert result_1["status"] == "OK"
    assert result_1["order_id"] == "OP-2026-3001"
    assert "OPCUA_OK" in result_1["dispatch"]
    assert "LEGACY_OK" in result_1["legacy_sync"]
    assert result_1["final_report"]["traceability_code"] == "LOT-OP-2026-3001"
    assert result_1["final_report"]["oee"] > 0
    assert result_1["pattern_trace"]["singleton"] == "MESController"
    assert len(result_1["implementation_map"]) == 10
    used_patterns_1 = {entry["pattern"] for entry in result_1["execution_log"]}
    assert {
        "Singleton",
        "Factory Method",
        "Abstract Factory",
        "Builder",
        "Adapter",
        "Prototype",
        "Bridge",
        "Decorator",
        "Composite",
        "Facade",
    }.issubset(used_patterns_1)

    result_2 = app.execute_order(
        OrderExecutionRequest(
            template_key="robot_packaging",
            order_id="OP-2026-3002",
            planned_units=400,
            shift="NIGHT",
            protocol="modbus",
        )
    )

    assert result_2["status"] == "OK"
    assert "MODBUS_OK" in result_2["dispatch"]
    assert result_2["controller_summary"]["closed_orders"] == 2
    assert result_2["controller_summary"]["global_oee"] > 0

    print("MES functional integration test: OK")
    print(result_1["controller_summary"])
    print(result_2["controller_summary"])


if __name__ == "__main__":
    run_mes_functional_test()
