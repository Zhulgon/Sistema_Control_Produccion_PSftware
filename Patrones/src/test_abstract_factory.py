"""
Prueba conceptual del patrón Abstract Factory para el caso MES.

Ejecución:
python test_abstract_factory.py
"""

from abstract_factory_production import AutomaticLineFactory, ManualLineFactory


def run_abstract_factory_test():
    automatic_factory = AutomaticLineFactory()
    manual_factory = ManualLineFactory()

    automatic_machine = automatic_factory.create_machine()
    automatic_robot = automatic_factory.create_robot()
    manual_machine = manual_factory.create_machine()
    manual_robot = manual_factory.create_robot()

    assert automatic_machine.operate() == "CNC Machine operating"
    assert automatic_robot.assist() == "Industrial robot assisting"
    assert manual_machine.operate() == "Manual machine operating"
    assert manual_robot.assist() == "Human operator assisting"

    print("Abstract Factory test conceptual: OK")
    print(f"Automatic line -> {automatic_machine.operate()} | {automatic_robot.assist()}")
    print(f"Manual line -> {manual_machine.operate()} | {manual_robot.assist()}")


if __name__ == "__main__":
    run_abstract_factory_test()
