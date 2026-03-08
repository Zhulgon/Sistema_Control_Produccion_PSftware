from abc import ABC, abstractmethod


# ===== Abstract Products =====

class Machine(ABC):
    @abstractmethod
    def operate(self):
        pass


class Robot(ABC):
    @abstractmethod
    def assist(self):
        pass


# ===== Concrete Products =====

class CNCMachine(Machine):
    def operate(self):
        return "CNC Machine operating"


class ManualMachine(Machine):
    def operate(self):
        return "Manual machine operating"


class IndustrialRobot(Robot):
    def assist(self):
        return "Industrial robot assisting"


class HumanOperator(Robot):
    def assist(self):
        return "Human operator assisting"


# ===== Abstract Factory =====

class ProductionLineFactory(ABC):

    @abstractmethod
    def create_machine(self):
        pass

    @abstractmethod
    def create_robot(self):
        pass


# ===== Concrete Factories =====

class AutomaticLineFactory(ProductionLineFactory):

    def create_machine(self):
        return CNCMachine()

    def create_robot(self):
        return IndustrialRobot()


class ManualLineFactory(ProductionLineFactory):

    def create_machine(self):
        return ManualMachine()

    def create_robot(self):
        return HumanOperator()