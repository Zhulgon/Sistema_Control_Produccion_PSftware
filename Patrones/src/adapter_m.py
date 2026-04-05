"""
Adapter - Integracion MES con gateway legacy

Proposito:
- Permitir que el MES use una interfaz moderna sin modificar un sistema legacy.
- Traducir datos de produccion entre formatos incompatibles.
"""
from abc import ABC, abstractmethod


class ProductionTrackingService(ABC):

    @abstractmethod
    def report_units(self, order_id: str, production_line: str, units: int) -> str:
        pass


class LegacyMachineGateway:

    def send_production_data(self, legacy_order_ref: str, legacy_line_code: str, produced_qty: int) -> str:
        return (
            f"LEGACY_OK order_ref={legacy_order_ref} "
            f"line={legacy_line_code} qty={produced_qty}"
        )


class LegacyMachineAdapter(ProductionTrackingService):

    def __init__(self, adaptee: LegacyMachineGateway):
        self._adaptee = adaptee

    def report_units(self, order_id: str, production_line: str, units: int) -> str:
        legacy_order_ref = order_id.replace("-", "")
        legacy_line_code = production_line.upper().replace("-", "_")
        return self._adaptee.send_production_data(legacy_order_ref, legacy_line_code, units)


class MESProductionClient:

    def __init__(self, tracking_service: ProductionTrackingService):
        self._tracking_service = tracking_service

    def close_partial_report(self, order_id: str, production_line: str, units: int) -> str:
        return self._tracking_service.report_units(order_id, production_line, units)
