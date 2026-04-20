"""
Aplicacion funcional del caso MES (fase implementada y trazable).

Objetivo de este archivo:
1) Ejecutar una orden de produccion end-to-end.
2) Mostrar de forma explicita en que punto participa cada patron.
3) Dejar evidencia clara para sustentacion academica.
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


@dataclass
class PatternImplementation:
    pattern: str
    objective: str
    module: str
    key_classes: str
    usage_point: str


def pattern_implementation_map() -> list[PatternImplementation]:
    return [
        PatternImplementation(
            pattern="Singleton",
            objective="Controlar estado global unico del MES.",
            module="src/singleton_m.py",
            key_classes="MESController",
            usage_point="execute_order(): plan_production/register_execution/close_order",
        ),
        PatternImplementation(
            pattern="Factory Method",
            objective="Crear maquinas CNC o Robot sin acoplar cliente.",
            module="src/factory_m.py",
            key_classes="MachineFactory, CNCFactory, RobotFactory",
            usage_point="execute_order(): machine_factory.create_machine()",
        ),
        PatternImplementation(
            pattern="Abstract Factory",
            objective="Crear familias compatibles de linea (maquina+asistente).",
            module="src/abstract_factory_m.py",
            key_classes="ProductionLineFactory, AutomaticLineFactory, ManualLineFactory",
            usage_point="execute_order(): line_factory.create_machine()/create_robot()",
        ),
        PatternImplementation(
            pattern="Builder",
            objective="Construir reportes de produccion por pasos.",
            module="src/builder_m.py",
            key_classes="ReportDirector, StandardProductionReportBuilder",
            usage_point="execute_order(): build_standard_shift_report/build_report_with_alerts",
        ),
        PatternImplementation(
            pattern="Adapter",
            objective="Integrar gateway legacy con interfaz moderna.",
            module="src/adapter_m.py",
            key_classes="LegacyMachineAdapter, LegacyMachineGateway, MESProductionClient",
            usage_point="execute_order(): tracking_client.close_partial_report()",
        ),
        PatternImplementation(
            pattern="Prototype",
            objective="Clonar plantillas de orden sin reconstruir desde cero.",
            module="src/prototype_m.py",
            key_classes="TemplateRegistry, ProductionOrderTemplate, MESProductionPlanner",
            usage_point="execute_order(): planner.prepare_order()",
        ),
        PatternImplementation(
            pattern="Bridge",
            objective="Separar tipo de orden del protocolo de comunicacion.",
            module="src/bridge_m.py",
            key_classes="MESScheduler, CNCWorkOrder, RobotWorkOrder, OPCUAChannel, ModbusChannel",
            usage_point="execute_order(): scheduler.release_order()",
        ),
        PatternImplementation(
            pattern="Decorator",
            objective="Agregar calidad, trazabilidad y OEE al reporte base.",
            module="src/decorator_m.py",
            key_classes="MESShiftCloser, QualityDecorator, TraceabilityDecorator, OEEDecorator",
            usage_point="execute_order(): shift_closer.close_shift()",
        ),
        PatternImplementation(
            pattern="Composite",
            objective="Modelar planta/linea/estacion y calcular capacidad total.",
            module="src/composite_m.py",
            key_classes="ProductionGroup, MachineStation, MESCapacityService",
            usage_point="execute_order(): capacity_service.calculate_total_units()",
        ),
        PatternImplementation(
            pattern="Facade",
            objective="Simplificar inicio de orden desde un punto unico.",
            module="src/facade_m.py",
            key_classes="MESProductionFacade, MESOperatorConsole",
            usage_point="execute_order(): operator_console.run_startup()",
        ),
    ]


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

    def get_pattern_map(self) -> list[PatternImplementation]:
        return pattern_implementation_map()

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
        execution_log: list[dict[str, str]] = []

        # [PATTERN: PROTOTYPE] Clonacion de orden base.
        base_order = self._planner.prepare_order(
            template_key=request.template_key,
            order_id=request.order_id,
            planned_units=request.planned_units,
            shift=request.shift,
        )
        execution_log.append(
            {
                "step": "Clone production template",
                "pattern": "Prototype",
                "module": "src/prototype_m.py",
                "evidence": f"template={base_order.template_name}",
            }
        )

        machine_type = str(base_order.machine_profile.get("machine_type", "cnc")).lower()
        production_line = str(base_order.machine_profile.get("line", "line-a")).upper()
        line_mode = str(base_order.parameters.get("line_mode", "automatic")).lower()

        # [PATTERN: FACADE] Inicio simplificado de orden.
        startup_result = self._operator_console.run_startup(
            order_id=request.order_id,
            production_line=production_line,
            planned_units=request.planned_units,
        )
        execution_log.append(
            {
                "step": "Startup order",
                "pattern": "Facade",
                "module": "src/facade_m.py",
                "evidence": startup_result.get("status", "UNKNOWN"),
            }
        )
        if startup_result.get("status") != "OK":
            return {
                "status": "ERROR",
                "message": startup_result.get("message", "No fue posible iniciar la orden."),
                "execution_log": execution_log,
            }

        if line_mode not in self._line_factories:
            raise KeyError(f"Linea no soportada: {line_mode}")
        if machine_type not in self._machine_factories:
            raise KeyError(f"Tipo de maquina no soportado: {machine_type}")

        # [PATTERN: ABSTRACT FACTORY] Familia compatible para la linea.
        line_factory = self._line_factories[line_mode]
        line_machine = line_factory.create_machine()
        line_assistant = line_factory.create_robot()
        execution_log.append(
            {
                "step": "Create line family",
                "pattern": "Abstract Factory",
                "module": "src/abstract_factory_m.py",
                "evidence": f"{type(line_factory).__name__}",
            }
        )

        # [PATTERN: SINGLETON] Registro central de planificacion.
        self._controller.plan_production(
            order_id=request.order_id,
            production_line=production_line,
            planned_units=request.planned_units,
            machine_type=machine_type,
            shift=request.shift,
        )
        execution_log.append(
            {
                "step": "Plan order in controller",
                "pattern": "Singleton",
                "module": "src/singleton_m.py",
                "evidence": "plan_production()",
            }
        )

        # [PATTERN: FACTORY METHOD] Creacion de maquina concreta.
        machine_factory = self._machine_factories[machine_type]
        machine = machine_factory.create_machine()
        startup_machine = machine.start()
        produced_units = machine.produce(request.planned_units)
        downtime_minutes = max(0, request.planned_units - produced_units) // 8
        execution_log.append(
            {
                "step": "Instantiate machine",
                "pattern": "Factory Method",
                "module": "src/factory_m.py",
                "evidence": f"{type(machine_factory).__name__} -> {type(machine).__name__}",
            }
        )

        # [PATTERN: BRIDGE] Despacho desacoplado por protocolo.
        scheduler = self._build_dispatcher(machine_type=machine_type, protocol=request.protocol)
        dispatch_result = scheduler.release_order(
            order_id=request.order_id,
            production_line=production_line,
            units=request.planned_units,
        )
        execution_log.append(
            {
                "step": "Dispatch order",
                "pattern": "Bridge",
                "module": "src/bridge_m.py",
                "evidence": dispatch_result,
            }
        )

        # [PATTERN: ADAPTER] Traduccion a sistema legacy.
        legacy_sync = self._tracking_client.close_partial_report(
            order_id=request.order_id,
            production_line=production_line.lower(),
            units=produced_units,
        )
        execution_log.append(
            {
                "step": "Sync with legacy",
                "pattern": "Adapter",
                "module": "src/adapter_m.py",
                "evidence": legacy_sync,
            }
        )

        # [PATTERN: SINGLETON] Registro central de ejecucion.
        self._controller.register_execution(
            order_id=request.order_id,
            produced_units=produced_units,
            downtime_minutes=downtime_minutes,
        )
        execution_log.append(
            {
                "step": "Register execution metrics",
                "pattern": "Singleton",
                "module": "src/singleton_m.py",
                "evidence": "register_execution()",
            }
        )

        alerts: list[str] = []
        if produced_units < request.planned_units:
            alerts.append("Gap entre plan y produccion real")
        if downtime_minutes > 0:
            alerts.append("Tiempo de parada registrado")

        report_notes = (
            f"{startup_machine}; line={line_machine.operate()}; assistant={line_assistant.assist()}"
        )

        # [PATTERN: BUILDER] Construccion de reporte por etapas.
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
        execution_log.append(
            {
                "step": "Build production report",
                "pattern": "Builder",
                "module": "src/builder_m.py",
                "evidence": "ReportDirector build_*()",
            }
        )

        # [PATTERN: DECORATOR] Enriquecimiento incremental de reporte.
        decorated_report = self._shift_closer.close_shift(
            order_id=request.order_id,
            planned_units=request.planned_units,
            produced_units=produced_units,
        )
        execution_log.append(
            {
                "step": "Decorate report with quality/trace/oee",
                "pattern": "Decorator",
                "module": "src/decorator_m.py",
                "evidence": "MESShiftCloser + decorators",
            }
        )

        final_report = {
            **asdict(report),
            **decorated_report,
            "template_name": base_order.template_name,
        }

        # [PATTERN: SINGLETON] Cierre de orden consolidado.
        self._controller.close_order(request.order_id, final_report)

        # [PATTERN: COMPOSITE] Calculo jerarquico de capacidad.
        plant_capacity = self._capacity_service.calculate_total_units()
        execution_log.append(
            {
                "step": "Calculate plant capacity",
                "pattern": "Composite",
                "module": "src/composite_m.py",
                "evidence": f"total_units={plant_capacity}",
            }
        )

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
            "execution_log": execution_log,
            "implementation_map": [asdict(p) for p in self.get_pattern_map()],
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
