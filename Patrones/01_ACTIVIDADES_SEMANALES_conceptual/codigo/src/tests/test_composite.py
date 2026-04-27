"""
Prueba conceptual del patron Composite para el caso MES.

Ejecucion:
python test_composite.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from composite_m import MESCapacityService, MachineStation, ProductionGroup


def run_composite_test():
    line_a = ProductionGroup("LINE-A")
    line_a.add(MachineStation("CNC-01", planned_units=120))
    line_a.add(MachineStation("CNC-02", planned_units=80))

    line_b = ProductionGroup("LINE-B")
    line_b.add(MachineStation("ROBOT-01", planned_units=150))

    plant = ProductionGroup("PLANT-1")
    plant.add(line_a)
    plant.add(line_b)

    service = MESCapacityService(plant)
    total_units = service.calculate_total_units()
    structure = service.export_structure()

    assert total_units == 350
    assert "+ Group PLANT-1" in structure
    assert "+ Group LINE-A" in structure
    assert "- Machine CNC-01: units=120" in structure
    assert "- Machine ROBOT-01: units=150" in structure

    print("Composite test conceptual: OK")
    print(f"total_units={total_units}")
    print(structure)


if __name__ == "__main__":
    run_composite_test()
