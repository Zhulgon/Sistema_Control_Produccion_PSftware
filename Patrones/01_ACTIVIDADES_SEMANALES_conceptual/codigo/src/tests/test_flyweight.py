"""
Prueba conceptual del patron Flyweight para el caso MES.

Ejecucion:
python test_flyweight.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from flyweight_m import MachineProfileFactory, MESTelemetryBoard


def run_flyweight_test():
    factory = MachineProfileFactory()
    board = MESTelemetryBoard(factory)

    for minute in range(1, 7):
        board.capture_event(
            event_id=f"EVT-CNC-{minute}",
            order_id="OP-2026-1301",
            production_line="LINE-A",
            minute=minute,
            units=45 + minute,
            machine_type="CNC",
            protocol="OPCUA",
            quality_rule="DIMENSIONAL",
            nominal_rate=50,
        )

    for minute in range(1, 5):
        board.capture_event(
            event_id=f"EVT-ROB-{minute}",
            order_id="OP-2026-1302",
            production_line="LINE-B",
            minute=minute,
            units=30 + minute,
            machine_type="ROBOT",
            protocol="MODBUS",
            quality_rule="VISUAL",
            nominal_rate=35,
        )

    assert board.total_events() == 10
    assert board.shared_profiles() == 2
    assert board.estimated_objects_saved() == 8
    assert "CNC/OPCUA" in board.export_sample(1)[0]

    print("Flyweight test conceptual: OK")
    print(f"events={board.total_events()}")
    print(f"shared_profiles={board.shared_profiles()}")
    print(f"estimated_objects_saved={board.estimated_objects_saved()}")
    print(board.export_sample(3))


if __name__ == "__main__":
    run_flyweight_test()
