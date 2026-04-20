"""
Prueba conceptual del patron Decorator para el caso MES.

Ejecucion:
python test_decorator.py
"""

from decorator_m import (
    BaseProductionReport,
    MESShiftCloser,
    OEEDecorator,
    QualityDecorator,
    TraceabilityDecorator,
)


def run_decorator_test():
    base_report = BaseProductionReport()
    decorated_report = OEEDecorator(TraceabilityDecorator(QualityDecorator(base_report)))
    shift_closer = MESShiftCloser(decorated_report)

    result = shift_closer.close_shift(
        order_id="OP-2026-1001",
        planned_units=500,
        produced_units=460,
    )

    assert result["order_id"] == "OP-2026-1001"
    assert result["planned_units"] == 500
    assert result["produced_units"] == 460
    assert result["quality_checks"] == ["dimensional", "visual"]
    assert result["traceability_code"] == "LOT-OP-2026-1001"
    assert result["oee"] == 92.0

    base_only = base_report.build(order_id="OP-BASE", planned_units=100, produced_units=95)
    assert "quality_checks" not in base_only
    assert "traceability_code" not in base_only
    assert "oee" not in base_only

    print("Decorator test conceptual: OK")
    print(result)


if __name__ == "__main__":
    run_decorator_test()
