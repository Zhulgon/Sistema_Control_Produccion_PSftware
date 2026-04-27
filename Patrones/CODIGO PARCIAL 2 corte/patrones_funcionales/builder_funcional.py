"""
Builder - ProductionReport funcional

Proposito:
- Construir reportes de produccion paso a paso.
- Separar el proceso de construccion de la representacion final.

Este modulo se usa en el flujo funcional de mes_functional_app.py.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ProductionReport:
    order_id: str = ""
    production_line: str = ""
    shift: str = ""
    units_planned: int = 0
    units_produced: int = 0
    downtime_minutes: int = 0
    quality_alerts: list[str] = field(default_factory=list)
    operator_notes: str = ""


class ProductionReportBuilder(ABC):

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def set_header(self, order_id: str, production_line: str, shift: str):
        pass

    @abstractmethod
    def set_output(self, units_planned: int, units_produced: int, downtime_minutes: int):
        pass

    @abstractmethod
    def add_quality_alert(self, alert: str):
        pass

    @abstractmethod
    def set_operator_notes(self, notes: str):
        pass

    @abstractmethod
    def build(self) -> ProductionReport:
        pass


class StandardProductionReportBuilder(ProductionReportBuilder):

    def __init__(self):
        self.reset()

    def reset(self):
        self._report = ProductionReport()

    def set_header(self, order_id: str, production_line: str, shift: str):
        self._report.order_id = order_id
        self._report.production_line = production_line
        self._report.shift = shift

    def set_output(self, units_planned: int, units_produced: int, downtime_minutes: int):
        self._report.units_planned = units_planned
        self._report.units_produced = units_produced
        self._report.downtime_minutes = downtime_minutes

    def add_quality_alert(self, alert: str):
        self._report.quality_alerts.append(alert)

    def set_operator_notes(self, notes: str):
        self._report.operator_notes = notes

    def build(self) -> ProductionReport:
        report = self._report
        self.reset()
        return report


class ReportDirector:

    def __init__(self, builder: ProductionReportBuilder):
        self._builder = builder

    def build_standard_shift_report(
        self,
        order_id: str,
        production_line: str,
        shift: str,
        units_planned: int,
        units_produced: int,
        downtime_minutes: int,
        notes: str,
    ) -> ProductionReport:
        self._builder.reset()
        self._builder.set_header(order_id, production_line, shift)
        self._builder.set_output(units_planned, units_produced, downtime_minutes)
        self._builder.set_operator_notes(notes)
        return self._builder.build()

    def build_report_with_alerts(
        self,
        order_id: str,
        production_line: str,
        shift: str,
        units_planned: int,
        units_produced: int,
        downtime_minutes: int,
        notes: str,
        alerts: list[str],
    ) -> ProductionReport:
        self._builder.reset()
        self._builder.set_header(order_id, production_line, shift)
        self._builder.set_output(units_planned, units_produced, downtime_minutes)
        for alert in alerts:
            self._builder.add_quality_alert(alert)
        self._builder.set_operator_notes(notes)
        return self._builder.build()


def run_demo() -> dict:
    director = ReportDirector(StandardProductionReportBuilder())
    report = director.build_report_with_alerts(
        order_id="OP-2026-FUNC-BUI",
        production_line="LINE-A",
        shift="DAY",
        units_planned=600,
        units_produced=570,
        downtime_minutes=3,
        notes="Reporte construido desde Builder funcional.",
        alerts=["Gap entre plan y produccion real"],
    )
    return report.__dict__


if __name__ == "__main__":
    print(run_demo())
