"""
Prototype - Plantillas de orden de produccion para MES

Proposito:
- Clonar configuraciones base de produccion sin reconstruirlas desde cero.
- Reducir costo de creacion cuando hay parametros repetidos por tipo de orden.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any


class Prototype(ABC):

    @abstractmethod
    def clone(self) -> "Prototype":
        pass


class ProductionOrderTemplate(Prototype):

    def __init__(
        self,
        template_name: str,
        machine_profile: dict[str, Any],
        quality_checks: list[str],
        parameters: dict[str, Any],
    ):
        self.template_name = template_name
        self.machine_profile = machine_profile
        self.quality_checks = quality_checks
        self.parameters = parameters
        self.order_id: str | None = None
        self.planned_units: int | None = None
        self.shift: str | None = None

    def clone(self) -> "ProductionOrderTemplate":
        return copy.deepcopy(self)

    def configure_for_order(
        self,
        order_id: str,
        planned_units: int,
        shift: str,
    ) -> "ProductionOrderTemplate":
        configured = self.clone()
        configured.order_id = order_id
        configured.planned_units = planned_units
        configured.shift = shift
        return configured

    def summary(self) -> str:
        return (
            f"template={self.template_name} "
            f"order={self.order_id} "
            f"line={self.machine_profile.get('line')} "
            f"units={self.planned_units} "
            f"shift={self.shift}"
        )


class TemplateRegistry:

    def __init__(self):
        self._templates: dict[str, ProductionOrderTemplate] = {}

    def register(self, key: str, template: ProductionOrderTemplate) -> None:
        self._templates[key] = template

    def create(self, key: str) -> ProductionOrderTemplate:
        if key not in self._templates:
            raise KeyError(f"Template '{key}' no registrado.")
        return self._templates[key].clone()


class MESProductionPlanner:

    def __init__(self, registry: TemplateRegistry):
        self._registry = registry

    def prepare_order(
        self,
        template_key: str,
        order_id: str,
        planned_units: int,
        shift: str,
    ) -> ProductionOrderTemplate:
        base = self._registry.create(template_key)
        return base.configure_for_order(order_id, planned_units, shift)


def run_demo() -> dict:
    registry = TemplateRegistry()
    template = ProductionOrderTemplate(
        template_name="CNC_STANDARD",
        machine_profile={"machine_type": "cnc", "line": "line-a", "program": "P-ALU-01"},
        quality_checks=["dimension_check", "surface_check"],
        parameters={"speed_rpm": 1800, "line_mode": "automatic"},
    )
    registry.register("cnc_standard", template)
    planner = MESProductionPlanner(registry)
    order = planner.prepare_order("cnc_standard", "OP-2026-FUNC-PRO", 600, "DAY")
    order.machine_profile["line"] = "line-b"
    return {"template_original_line": template.machine_profile["line"], "cloned_order": order.summary()}


if __name__ == "__main__":
    print(run_demo())
