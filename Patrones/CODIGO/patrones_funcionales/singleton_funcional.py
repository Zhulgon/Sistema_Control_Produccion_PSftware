from __future__ import annotations

"""
Singleton - Controlador central del MES.

Este modulo mantiene una unica instancia de MESController y concentra
estado operativo de ordenes, produccion y metricas globales.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PlannedOrder:
    order_id: str
    production_line: str
    planned_units: int
    machine_type: str
    shift: str


class MESController:
    _instance: "MESController | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MESController, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._planned_orders: dict[str, PlannedOrder] = {}
        self._closed_reports: list[dict[str, Any]] = []
        self._totals = {
            "planned_units": 0,
            "produced_units": 0,
            "downtime_minutes": 0,
        }

    def reset(self) -> None:
        self._planned_orders.clear()
        self._closed_reports.clear()
        self._totals = {
            "planned_units": 0,
            "produced_units": 0,
            "downtime_minutes": 0,
        }

    def plan_production(
        self,
        order_id: str,
        production_line: str,
        planned_units: int,
        machine_type: str,
        shift: str,
    ) -> PlannedOrder:
        order = PlannedOrder(
            order_id=order_id,
            production_line=production_line,
            planned_units=planned_units,
            machine_type=machine_type,
            shift=shift,
        )
        self._planned_orders[order_id] = order
        self._totals["planned_units"] += planned_units
        return order

    def register_execution(
        self,
        order_id: str,
        produced_units: int,
        downtime_minutes: int,
    ) -> None:
        if order_id not in self._planned_orders:
            raise KeyError(f"Orden no planificada: {order_id}")
        self._totals["produced_units"] += produced_units
        self._totals["downtime_minutes"] += downtime_minutes

    def close_order(self, order_id: str, final_report: dict[str, Any]) -> None:
        if order_id in self._planned_orders:
            del self._planned_orders[order_id]
        self._closed_reports.append(final_report)

    def calculate_oee(self) -> float:
        planned = self._totals["planned_units"]
        if planned <= 0:
            return 0.0
        return round((self._totals["produced_units"] / planned) * 100, 2)

    def summary(self) -> dict[str, Any]:
        return {
            "active_orders": len(self._planned_orders),
            "closed_orders": len(self._closed_reports),
            "planned_units_total": self._totals["planned_units"],
            "produced_units_total": self._totals["produced_units"],
            "downtime_minutes_total": self._totals["downtime_minutes"],
            "global_oee": self.calculate_oee(),
        }


def run_demo() -> dict:
    controller_a = MESController()
    controller_b = MESController()
    controller_a.reset()
    controller_a.plan_production("OP-2026-FUNC-SIN", "LINE-A", 500, "cnc", "DAY")
    controller_b.register_execution("OP-2026-FUNC-SIN", 475, 4)
    controller_a.close_order("OP-2026-FUNC-SIN", {"status": "OK", "oee": controller_b.calculate_oee()})
    return {"same_instance": controller_a is controller_b, "summary": controller_b.summary()}


if __name__ == "__main__":
    print(run_demo())
