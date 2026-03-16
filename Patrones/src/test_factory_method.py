"""
Prueba conceptual del patrón Factory Method para el caso MES.

Ejecución:
python test_factory_method.py
"""

from factory_machines import CNCFactory, CNCMachine, RobotFactory, RobotMachine


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
