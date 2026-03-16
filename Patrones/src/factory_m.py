"""
Factory Method - Creación de máquinas

Propósito:
- Desacoplar la creación de equipos industriales.
- Permitir extensión sin modificar código existente.
"""

from abc import ABC, abstractmethod


class Machine(ABC):

    @abstractmethod
    def start(self):
        pass


class CNCMachine(Machine):

    def start(self):
        pass


class RobotMachine(Machine):

    def start(self):
        pass


class MachineFactory(ABC):

    @abstractmethod
    def create_machine(self) -> Machine:
        pass

    def start_machine(self):
        machine = self.create_machine()
        machine.start()


class CNCFactory(MachineFactory):

    def create_machine(self) -> Machine:
        return CNCMachine()


class RobotFactory(MachineFactory):

    def create_machine(self) -> Machine:
        return RobotMachine()