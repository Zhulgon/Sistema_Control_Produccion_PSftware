"""
Aplicacion funcional del caso MES (fase implementada).

Integra los patrones trabajados:
Singleton, Factory Method, Abstract Factory, Builder, Adapter,
Prototype, Bridge, Decorator, Composite y Facade.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from abstract_factory_m import AutomaticLineFactory, ManualLineFactory, ProductionLineFactory
from adapter_m import LegacyMachineAdapter, LegacyMachineGateway, MESProductionClient
from bridge_m import CNCWorkOrder, MESScheduler, ModbusChannel, OPCUAChannel, RobotWorkOrder
from builder_m import ReportDirector, StandardProductionReportBuilder
from composite_m import MESCapacityService, MachineStation, ProductionGroup
from decorator_m import (
    BaseProductionReport,
    MESShiftCloser,
    OEEDecorator,
    QualityDecorator,
    TraceabilityDecorator,
)
from facade_m import MESOperatorConsole, MESProductionFacade
from factory_m import CNCFactory, MachineFactory, RobotFactory
from prototype_m import MESProductionPlanner, ProductionOrderTemplate, TemplateRegistry
from singleton_m import MESController


@dataclass
class OrderExecutionRequest:
    template_key: str
    order_id: str
    planned_units: int
    shift: str
    protocol: str = "opcua"


class FunctionalMESProject:
    def __init__(
        self,
        controller: MESController,
        planner: MESProductionPlanner,
        capacity_service: MESCapacityService,
        operator_console: MESOperatorConsole,
        tracking_client: MESProductionClient,
        report_director: ReportDirector,
    ):
        self._controller = controller
        self._planner = planner
        self._capacity_service = capacity_service
        self._operator_console = operator_console
        self._tracking_client = tracking_client
        self._report_director = report_director
        self._shift_closer = MESShiftCloser(
            OEEDecorator(TraceabilityDecorator(QualityDecorator(BaseProductionReport())))
        )

        self._line_factories: dict[str, ProductionLineFactory] = {
            "automatic": AutomaticLineFactory(),
            "manual": ManualLineFactory(),
        }
        self._machine_factories: dict[str, MachineFactory] = {
            "cnc": CNCFactory(),
            "robot": RobotFactory(),
        }

    def _build_dispatcher(self, machine_type: str, protocol: str) -> MESScheduler:
        protocol_key = protocol.lower()
        if protocol_key == "modbus":
            channel = ModbusChannel()
        else:
            channel = OPCUAChannel()

        if machine_type.lower() == "cnc":
            work_order = CNCWorkOrder(channel)
        else:
            work_order = RobotWorkOrder(channel)

        return MESScheduler(work_order)

    def execute_order(self, request: OrderExecutionRequest) -> dict[str, Any]:
        base_order = self._planner.prepare_order(
            template_key=request.template_key,
            order_id=request.order_id,
            planned_units=request.planned_units,
            shift=request.shift,
        )

        machine_type = str(base_order.machine_profile.get("machine_type", "cnc")).lower()
        production_line = str(base_order.machine_profile.get("line", "line-a")).upper()
        line_mode = str(base_order.parameters.get("line_mode", "automatic")).lower()

        startup_result = self._operator_console.run_startup(
            order_id=request.order_id,
            production_line=production_line,
            planned_units=request.planned_units,
        )
        if startup_result.get("status") != "OK":
            return {
                "status": "ERROR",
                "message": startup_result.get("message", "No fue posible iniciar la orden."),
            }

        if line_mode not in self._line_factories:
            raise KeyError(f"Linea no soportada: {line_mode}")
        if machine_type not in self._machine_factories:
            raise KeyError(f"Tipo de maquina no soportado: {machine_type}")

        line_factory = self._line_factories[line_mode]
        line_machine = line_factory.create_machine()
        line_assistant = line_factory.create_robot()

        self._controller.plan_production(
            order_id=request.order_id,
            production_line=production_line,
            planned_units=request.planned_units,
            machine_type=machine_type,
            shift=request.shift,
        )

        machine_factory = self._machine_factories[machine_type]
        machine = machine_factory.create_machine()
        startup_machine = machine.start()
        produced_units = machine.produce(request.planned_units)
        downtime_minutes = max(0, request.planned_units - produced_units) // 8

        scheduler = self._build_dispatcher(machine_type=machine_type, protocol=request.protocol)
        dispatch_result = scheduler.release_order(
            order_id=request.order_id,
            production_line=production_line,
            units=request.planned_units,
        )

        legacy_sync = self._tracking_client.close_partial_report(
            order_id=request.order_id,
            production_line=production_line.lower(),
            units=produced_units,
        )

        self._controller.register_execution(
            order_id=request.order_id,
            produced_units=produced_units,
            downtime_minutes=downtime_minutes,
        )

        alerts: list[str] = []
        if produced_units < request.planned_units:
            alerts.append("Gap entre plan y produccion real")
        if downtime_minutes > 0:
            alerts.append("Tiempo de parada registrado")

        report_notes = (
            f"{startup_machine}; line={line_machine.operate()}; assistant={line_assistant.assist()}"
        )
        if alerts:
            report = self._report_director.build_report_with_alerts(
                order_id=request.order_id,
                production_line=production_line,
                shift=request.shift,
                units_planned=request.planned_units,
                units_produced=produced_units,
                downtime_minutes=downtime_minutes,
                notes=report_notes,
                alerts=alerts,
            )
        else:
            report = self._report_director.build_standard_shift_report(
                order_id=request.order_id,
                production_line=production_line,
                shift=request.shift,
                units_planned=request.planned_units,
                units_produced=produced_units,
                downtime_minutes=downtime_minutes,
                notes=report_notes,
            )

        decorated_report = self._shift_closer.close_shift(
            order_id=request.order_id,
            planned_units=request.planned_units,
            produced_units=produced_units,
        )

        final_report = {
            **asdict(report),
            **decorated_report,
            "template_name": base_order.template_name,
        }

        self._controller.close_order(request.order_id, final_report)

        plant_capacity = self._capacity_service.calculate_total_units()

        return {
            "status": "OK",
            "order_id": request.order_id,
            "startup": startup_result,
            "dispatch": dispatch_result,
            "legacy_sync": legacy_sync,
            "final_report": final_report,
            "controller_summary": self._controller.summary(),
            "plant_capacity_units": plant_capacity,
            "pattern_trace": {
                "singleton": "MESController",
                "factory_method": type(machine_factory).__name__,
                "abstract_factory": type(line_factory).__name__,
                "builder": type(self._report_director).__name__,
                "adapter": "LegacyMachineAdapter",
                "prototype": base_order.template_name,
                "bridge": request.protocol.lower(),
                "decorator": "OEEDecorator+TraceabilityDecorator+QualityDecorator",
                "composite": "MESCapacityService",
                "facade": "MESProductionFacade",
            },
        }


def build_default_mes_project() -> FunctionalMESProject:
    controller = MESController()
    controller.reset()

    registry = TemplateRegistry()
    registry.register(
        "cnc_standard",
        ProductionOrderTemplate(
            template_name="CNC_STANDARD",
            machine_profile={
                "machine_type": "cnc",
                "line": "line-a",
                "program": "P-ALU-01",
            },
            quality_checks=["dimension_check", "surface_check"],
            parameters={"speed_rpm": 1800, "line_mode": "automatic"},
        ),
    )
    registry.register(
        "robot_packaging",
        ProductionOrderTemplate(
            template_name="ROBOT_PACKAGING",
            machine_profile={
                "machine_type": "robot",
                "line": "line-b",
                "program": "R-PACK-03",
            },
            quality_checks=["seal_check", "label_check"],
            parameters={"grip_force": 45, "line_mode": "manual"},
        ),
    )

    planner = MESProductionPlanner(registry)

    line_a = ProductionGroup("LINE-A")
    line_a.add(MachineStation("CNC-01", planned_units=800))
    line_a.add(MachineStation("CNC-02", planned_units=700))

    line_b = ProductionGroup("LINE-B")
    line_b.add(MachineStation("ROBOT-01", planned_units=500))
    line_b.add(MachineStation("ROBOT-02", planned_units=450))

    plant = ProductionGroup("PLANT-MES")
    plant.add(line_a)
    plant.add(line_b)

    capacity_service = MESCapacityService(plant)

    facade = MESProductionFacade()
    operator_console = MESOperatorConsole(facade)

    adapter = LegacyMachineAdapter(LegacyMachineGateway())
    tracking_client = MESProductionClient(adapter)

    report_builder = StandardProductionReportBuilder()
    report_director = ReportDirector(report_builder)

    return FunctionalMESProject(
        controller=controller,
        planner=planner,
        capacity_service=capacity_service,
        operator_console=operator_console,
        tracking_client=tracking_client,
        report_director=report_director,
    )


def run_demo() -> dict[str, Any]:
    app = build_default_mes_project()
    return app.execute_order(
        OrderExecutionRequest(
            template_key="cnc_standard",
            order_id="OP-2026-2001",
            planned_units=600,
            shift="DAY",
            protocol="opcua",
        )
    )


if __name__ == "__main__":
    result = run_demo()
    print(result)
