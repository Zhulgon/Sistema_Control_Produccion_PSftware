"""
Prueba conceptual del patrón Factory Method para el caso MES.

Ejecución:
python test_factory_method.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from factory_m import CNCFactory, CNCMachine, RobotFactory, RobotMachine


def run_factory_method_test():
    cnc_factory = CNCFactory()
    robot_factory = RobotFactory()

    cnc_machine = cnc_factory.create_machine()
    robot_machine = robot_factory.create_machine()

    assert isinstance(cnc_machine, CNCMachine)
    assert isinstance(robot_machine, RobotMachine)

    print("Factory Method test conceptual: OK")
    print(f"CNCFactory -> {type(cnc_machine).__name__}")
    print(f"RobotFactory -> {type(robot_machine).__name__}")


if __name__ == "__main__":
    run_factory_method_test()
