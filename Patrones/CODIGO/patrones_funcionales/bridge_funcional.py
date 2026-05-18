"""
Bridge - Despacho de ordenes de produccion en MES

Proposito:
- Separar el tipo de orden del canal de comunicacion.
- Permitir combinar ordenes y protocolos sin acoplar jerarquias.
"""

from abc import ABC, abstractmethod


class CommunicationChannel(ABC):

    @abstractmethod
    def transmit(self, production_line: str, payload: str) -> str:
        pass


class OPCUAChannel(CommunicationChannel):

    def transmit(self, production_line: str, payload: str) -> str:
        return f"OPCUA_OK line={production_line} payload={payload}"


class ModbusChannel(CommunicationChannel):

    def transmit(self, production_line: str, payload: str) -> str:
        return f"MODBUS_OK line={production_line} payload={payload}"


class WorkOrder(ABC):

    def __init__(self, channel: CommunicationChannel):
        self._channel = channel

    @abstractmethod
    def dispatch(self, order_id: str, production_line: str, units: int) -> str:
        pass


class CNCWorkOrder(WorkOrder):

    def dispatch(self, order_id: str, production_line: str, units: int) -> str:
        payload = f"CNC|order={order_id}|units={units}"
        return self._channel.transmit(production_line, payload)


class RobotWorkOrder(WorkOrder):

    def dispatch(self, order_id: str, production_line: str, units: int) -> str:
        payload = f"ROBOT|order={order_id}|units={units}"
        return self._channel.transmit(production_line, payload)


class MESScheduler:

    def __init__(self, work_order: WorkOrder):
        self._work_order = work_order

    def release_order(self, order_id: str, production_line: str, units: int) -> str:
        return self._work_order.dispatch(order_id, production_line, units)


def run_demo() -> dict:
    cnc_scheduler = MESScheduler(CNCWorkOrder(OPCUAChannel()))
    robot_scheduler = MESScheduler(RobotWorkOrder(ModbusChannel()))
    return {
        "cnc_opcua": cnc_scheduler.release_order("OP-2026-FUNC-BRI", "LINE-A", 600),
        "robot_modbus": robot_scheduler.release_order("OP-2026-FUNC-BRI2", "LINE-B", 420),
    }


if __name__ == "__main__":
    print(run_demo())
