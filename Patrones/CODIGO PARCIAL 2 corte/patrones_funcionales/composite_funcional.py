"""
Composite - Estructura jerarquica de planta MES

Proposito:
- Tratar de forma uniforme una maquina individual y un grupo de maquinas.
- Calcular capacidad y estructura de produccion sobre arboles de nodos.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProductionNode(ABC):

    @abstractmethod
    def total_planned_units(self) -> int:
        pass

    @abstractmethod
    def summary(self, depth: int = 0) -> str:
        pass


class MachineStation(ProductionNode):

    def __init__(self, name: str, planned_units: int):
        self.name = name
        self.planned_units = planned_units

    def total_planned_units(self) -> int:
        return self.planned_units

    def summary(self, depth: int = 0) -> str:
        indent = "  " * depth
        return f"{indent}- Machine {self.name}: units={self.planned_units}"


class ProductionGroup(ProductionNode):

    def __init__(self, name: str):
        self.name = name
        self._children: list[ProductionNode] = []

    def add(self, node: ProductionNode) -> None:
        self._children.append(node)

    def remove(self, node: ProductionNode) -> None:
        self._children.remove(node)

    def total_planned_units(self) -> int:
        return sum(child.total_planned_units() for child in self._children)

    def summary(self, depth: int = 0) -> str:
        indent = "  " * depth
        lines = [f"{indent}+ Group {self.name}"]
        for child in self._children:
            lines.append(child.summary(depth + 1))
        return "\n".join(lines)


class MESCapacityService:

    def __init__(self, root: ProductionNode):
        self._root = root

    def calculate_total_units(self) -> int:
        return self._root.total_planned_units()

    def export_structure(self) -> str:
        return self._root.summary()


def run_demo() -> dict:
    line_a = ProductionGroup("LINE-A")
    line_a.add(MachineStation("CNC-01", 800))
    line_a.add(MachineStation("CNC-02", 700))
    line_b = ProductionGroup("LINE-B")
    line_b.add(MachineStation("ROBOT-01", 500))
    plant = ProductionGroup("PLANT-MES")
    plant.add(line_a)
    plant.add(line_b)
    service = MESCapacityService(plant)
    return {"total_units": service.calculate_total_units(), "structure": service.export_structure()}


if __name__ == "__main__":
    print(run_demo())
