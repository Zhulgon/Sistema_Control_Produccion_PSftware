# 9. Patron Bridge aplicado al MES

## 9.1 Problema

El MES debe despachar ordenes a distintas lineas y protocolos industriales. En este caso pueden variar dos dimensiones:

- Tipo de orden de produccion (CNC, Robot, etc.).
- Canal de comunicacion industrial (OPC UA, Modbus, etc.).

Si cada tipo de orden conoce todos los protocolos, se genera:

- Acoplamiento fuerte entre dominio y comunicacion.
- Explosion de clases por combinaciones.
- Mayor costo de mantenimiento al agregar un nuevo protocolo.

## 9.2 Solucion (aplicacion del patron)

Se aplica **Bridge** para separar la abstraccion de orden de produccion de la implementacion de comunicacion.

### Elementos del patron en este caso

- **Abstraction:** `WorkOrder`
- **Refined Abstractions:** `CNCWorkOrder`, `RobotWorkOrder`
- **Implementor:** `CommunicationChannel`
- **Concrete Implementors:** `OPCUAChannel`, `ModbusChannel`

Cada `WorkOrder` delega el envio del mensaje al `CommunicationChannel` inyectado.

## 9.3 Justificacion

Bridge se justifica porque:

- Permite evolucionar ordenes y protocolos de forma independiente.
- Evita condicionales por protocolo dentro de cada tipo de orden.
- Reduce impacto de cambios al incorporar nuevas tecnologias de planta.

## 9.4 Evidencia del patron

Para evidenciar Bridge se usa:

- Composicion entre `WorkOrder` y `CommunicationChannel`.
- Dos jerarquias independientes combinables en tiempo de ejecucion.

**UML:** `Patrones/docs/diagrams/bridge.puml`  
**Python conceptual:** `Patrones/src/bridge_m.py`

## 9.5 Extension

Si se agrega un nuevo canal (ej: `MQTTChannel`), solo se implementa `CommunicationChannel` sin modificar `CNCWorkOrder` ni `RobotWorkOrder`.
