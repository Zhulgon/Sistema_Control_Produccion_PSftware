"""
Prueba conceptual del patron Facade para el caso MES.

Ejecucion:
python test_facade.py
"""

from facade_m import MESOperatorConsole, MESProductionFacade


def run_facade_test():
    facade = MESProductionFacade()
    console = MESOperatorConsole(facade)

    ok_result = console.run_startup(
        order_id="OP-2026-1101",
        production_line="LINE-C",
        planned_units=600,
    )

    assert ok_result["status"] == "OK"
    assert ok_result["order_id"] == "OP-2026-1101"
    assert ok_result["line"] == "LINE-C"
    assert len(ok_result["steps"]) == 4
    assert "materials_reserved" in ok_result["steps"][0]
    assert "batch_opened" in ok_result["steps"][3]

    error_result = console.run_startup(
        order_id="INVALID-ORDER",
        production_line="LINE-C",
        planned_units=0,
    )

    assert error_result["status"] == "ERROR"
    assert "Orden invalida" in error_result["message"]

    print("Facade test conceptual: OK")
    print(ok_result)
    print(error_result)


if __name__ == "__main__":
    run_facade_test()
