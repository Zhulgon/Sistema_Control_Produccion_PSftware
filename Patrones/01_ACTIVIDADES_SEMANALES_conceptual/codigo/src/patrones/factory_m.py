"""
Factory Method - Creacion de maquinas para el MES.

La fabrica desacopla al cliente de la clase concreta de maquina.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Machine(ABC):

    @abstractmethod
    def start(self) -> str:
        pass

    @abstractmethod
    def produce(self, planned_units: int) -> int:
        pass


class CNCMachine(Machine):

    def start(self) -> str:
        return "CNC machine started"

    def produce(self, planned_units: int) -> int:
        # CNC suele tener alta precision y rendimiento estable.
        return max(0, int(planned_units * 0.95))


class RobotMachine(Machine):

    def start(self) -> str:
        return "Robot cell started"

    def produce(self, planned_units: int) -> int:
        # Celda robotica con variacion por calibracion.
        return max(0, int(planned_units * 0.92))


class MachineFactory(ABC):

    @abstractmethod
    def create_machine(self) -> Machine:
        pass

    def start_machine(self) -> str:
        machine = self.create_machine()
        return machine.start()


class CNCFactory(MachineFactory):

    def create_machine(self) -> Machine:
        return CNCMachine()


class RobotFactory(MachineFactory):

    def create_machine(self) -> Machine:
        return RobotMachine()
