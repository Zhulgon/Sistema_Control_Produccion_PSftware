"""
Facade - Inicio simplificado de orden en MES

Proposito:
- Ofrecer un punto unico para arrancar una orden de produccion.
- Encapsular coordinacion entre subsistemas tecnicos del MES.
"""

from __future__ import annotations

from typing import Any


class OrderValidator:

    def validate(self, order_id: str, planned_units: int) -> bool:
        return order_id.startswith("OP-") and planned_units > 0


class InventoryService:

    def reserve_material(self, order_id: str, planned_units: int) -> str:
        return f"materials_reserved order={order_id} units={planned_units}"


class MachinePreparationService:

    def prepare_line(self, production_line: str) -> str:
        return f"line_prepared line={production_line}"


class QualityService:

    def load_checklist(self, order_id: str) -> str:
        return f"quality_checklist_loaded order={order_id}"


class TrackingService:

    def open_batch(self, order_id: str, production_line: str) -> str:
        return f"batch_opened order={order_id} line={production_line}"


class MESProductionFacade:

    def __init__(
        self,
        validator: OrderValidator | None = None,
        inventory: InventoryService | None = None,
        preparation: MachinePreparationService | None = None,
        quality: QualityService | None = None,
        tracking: TrackingService | None = None,
    ):
        self._validator = validator or OrderValidator()
        self._inventory = inventory or InventoryService()
        self._preparation = preparation or MachinePreparationService()
        self._quality = quality or QualityService()
        self._tracking = tracking or TrackingService()

    def start_order(self, order_id: str, production_line: str, planned_units: int) -> dict[str, Any]:
        if not self._validator.validate(order_id, planned_units):
            return {
                "status": "ERROR",
                "message": "Orden invalida para iniciar produccion.",
            }

        steps = [
            self._inventory.reserve_material(order_id, planned_units),
            self._preparation.prepare_line(production_line),
            self._quality.load_checklist(order_id),
            self._tracking.open_batch(order_id, production_line),
        ]

        return {
            "status": "OK",
            "order_id": order_id,
            "line": production_line,
            "planned_units": planned_units,
            "steps": steps,
        }


class MESOperatorConsole:

    def __init__(self, facade: MESProductionFacade):
        self._facade = facade

    def run_startup(self, order_id: str, production_line: str, planned_units: int) -> dict[str, Any]:
        return self._facade.start_order(order_id, production_line, planned_units)
