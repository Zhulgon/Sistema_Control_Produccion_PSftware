"""
Prueba conceptual del patron Prototype para el caso MES.

Ejecucion:
python test_prototype.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from prototype_m import MESProductionPlanner, ProductionOrderTemplate, TemplateRegistry


def run_prototype_test():
    cnc_template = ProductionOrderTemplate(
        template_name="CNC_STANDARD",
        machine_profile={
            "machine_type": "CNC",
            "line": "line-a",
            "program": "P-ALU-01",
        },
        quality_checks=["dimension_check", "surface_check"],
        parameters={"speed_rpm": 1800, "coolant": "on"},
    )

    registry = TemplateRegistry()
    registry.register("cnc_standard", cnc_template)

    planner = MESProductionPlanner(registry)
    order_clone = planner.prepare_order(
        template_key="cnc_standard",
        order_id="OP-2026-0901",
        planned_units=450,
        shift="night",
    )

    # Cambios sobre el clon: no deben afectar la plantilla base.
    order_clone.machine_profile["line"] = "line-b"
    order_clone.quality_checks.append("vibration_check")
    order_clone.parameters["speed_rpm"] = 2100

    assert order_clone is not cnc_template
    assert order_clone.template_name == "CNC_STANDARD"
    assert order_clone.order_id == "OP-2026-0901"
    assert order_clone.planned_units == 450
    assert order_clone.shift == "night"

    assert cnc_template.machine_profile["line"] == "line-a"
    assert cnc_template.quality_checks == ["dimension_check", "surface_check"]
    assert cnc_template.parameters["speed_rpm"] == 1800

    print("Prototype test conceptual: OK")
    print(order_clone.summary())


if __name__ == "__main__":
    run_prototype_test()
