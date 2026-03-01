"""
Singleton - MESController (conceptual)

Propósito:
- Garantizar una única instancia del controlador central del MES.
- Evitar inconsistencias en planificación y métricas globales.

Este código es demostrativo.
"""

class MESController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MESController, cls).__new__(cls)
        return cls._instance

    def plan_production(self):
        pass

    def calculate_oee(self):
        pass