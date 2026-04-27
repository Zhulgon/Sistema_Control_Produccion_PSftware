"""
Decorator - Cierre de reportes de turno en MES

Proposito:
- Agregar responsabilidades a un reporte sin modificar la clase base.
- Componer capacidades de calidad, trazabilidad y OEE de forma flexible.
"""

from abc import ABC, abstractmethod
from typing import Any


class ProductionReport(ABC):

    @abstractmethod
    def build(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        pass


class BaseProductionReport(ProductionReport):

    def build(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        return {
            "order_id": order_id,
            "planned_units": planned_units,
            "produced_units": produced_units,
        }


class ReportDecorator(ProductionReport):

    def __init__(self, wrappee: ProductionReport):
        self._wrappee = wrappee

    def build(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        return self._wrappee.build(order_id, planned_units, produced_units)


class QualityDecorator(ReportDecorator):

    def build(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        report = super().build(order_id, planned_units, produced_units)
        report["quality_checks"] = ["dimensional", "visual"]
        return report


class TraceabilityDecorator(ReportDecorator):

    def build(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        report = super().build(order_id, planned_units, produced_units)
        report["traceability_code"] = f"LOT-{order_id}"
        return report


class OEEDecorator(ReportDecorator):

    def build(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        report = super().build(order_id, planned_units, produced_units)

        if planned_units <= 0:
            report["oee"] = 0.0
        else:
            report["oee"] = round((produced_units / planned_units) * 100, 2)

        return report


class MESShiftCloser:

    def __init__(self, report_builder: ProductionReport):
        self._report_builder = report_builder

    def close_shift(self, order_id: str, planned_units: int, produced_units: int) -> dict[str, Any]:
        return self._report_builder.build(order_id, planned_units, produced_units)


def run_demo() -> dict:
    report_builder = OEEDecorator(TraceabilityDecorator(QualityDecorator(BaseProductionReport())))
    closer = MESShiftCloser(report_builder)
    return closer.close_shift("OP-2026-FUNC-DEC", 600, 570)


if __name__ == "__main__":
    print(run_demo())
