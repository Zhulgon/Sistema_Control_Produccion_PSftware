"""
Prueba conceptual del patron Bridge para el caso MES.

Ejecucion:
python test_bridge.py
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from bridge_m import CNCWorkOrder, MESScheduler, ModbusChannel, OPCUAChannel, RobotWorkOrder


def run_bridge_test():
    cnc_scheduler = MESScheduler(CNCWorkOrder(OPCUAChannel()))
    robot_scheduler = MESScheduler(RobotWorkOrder(ModbusChannel()))

    cnc_result = cnc_scheduler.release_order(
        order_id="OP-2026-0901",
        production_line="line-a",
        units=120,
    )
    robot_result = robot_scheduler.release_order(
        order_id="OP-2026-0902",
        production_line="line-b",
        units=80,
    )

    assert "OPCUA_OK" in cnc_result
    assert "CNC|order=OP-2026-0901|units=120" in cnc_result
    assert "MODBUS_OK" in robot_result
    assert "ROBOT|order=OP-2026-0902|units=80" in robot_result

    print("Bridge test conceptual: OK")
    print(cnc_result)
    print(robot_result)


if __name__ == "__main__":
    run_bridge_test()
