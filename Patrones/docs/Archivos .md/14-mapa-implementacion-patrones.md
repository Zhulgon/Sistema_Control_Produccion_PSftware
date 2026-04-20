# Mapa de implementacion de patrones (fase funcional)

## 1. Para que sirve este documento

Responder rapido y sin ambiguedad estas preguntas:
- Cual es el alcance funcional real del proyecto.
- Donde esta implementado cada patron en el codigo.
- Que evidencia practica demuestra su uso en ejecucion.

## 2. Alcance funcional real

La fase funcional implementa el flujo end-to-end de una orden MES:
1. Clonar plantilla de orden.
2. Iniciar orden y validar prerequisitos.
3. Crear componentes de linea.
4. Ejecutar y despachar la orden.
5. Sincronizar datos con sistema legacy.
6. Construir y enriquecer reporte final.
7. Consolidar metricas globales y capacidad de planta.

## 3. Matriz patron -> implementacion

| Patron | Modulo principal | Clases clave | Punto de uso en flujo |
|---|---|---|---|
| Singleton | `src/singleton_m.py` | `MESController` | `plan_production()`, `register_execution()`, `close_order()` |
| Factory Method | `src/factory_m.py` | `MachineFactory`, `CNCFactory`, `RobotFactory` | `machine_factory.create_machine()` |
| Abstract Factory | `src/abstract_factory_m.py` | `ProductionLineFactory`, `AutomaticLineFactory`, `ManualLineFactory` | `line_factory.create_machine()/create_robot()` |
| Builder | `src/builder_m.py` | `ReportDirector`, `StandardProductionReportBuilder` | `build_standard_shift_report()/build_report_with_alerts()` |
| Adapter | `src/adapter_m.py` | `LegacyMachineAdapter`, `LegacyMachineGateway`, `MESProductionClient` | `tracking_client.close_partial_report()` |
| Prototype | `src/prototype_m.py` | `TemplateRegistry`, `ProductionOrderTemplate`, `MESProductionPlanner` | `planner.prepare_order()` |
| Bridge | `src/bridge_m.py` | `MESScheduler`, `CNCWorkOrder`, `RobotWorkOrder`, `OPCUAChannel`, `ModbusChannel` | `scheduler.release_order()` |
| Decorator | `src/decorator_m.py` | `MESShiftCloser`, `QualityDecorator`, `TraceabilityDecorator`, `OEEDecorator` | `shift_closer.close_shift()` |
| Composite | `src/composite_m.py` | `ProductionGroup`, `MachineStation`, `MESCapacityService` | `capacity_service.calculate_total_units()` |
| Facade | `src/facade_m.py` | `MESProductionFacade`, `MESOperatorConsole` | `operator_console.run_startup()` |

## 4. Archivo integrador

- `src/mes_functional_app.py`

Este archivo contiene:
- Mapa de implementacion por patron: `pattern_implementation_map()`
- Flujo de orden completo: `FunctionalMESProject.execute_order()`
- Bitacora de evidencia por patron: `execution_log`

## 5. Evidencia practica recomendada

```bash
cd Patrones/src
python run_practica_guiada.py
```

La salida muestra:
- Alcance funcional real.
- Mapa patron -> codigo.
- Bitacora de ejecucion paso a paso con modulo y patron usado.
- Resultado final y reporte.
