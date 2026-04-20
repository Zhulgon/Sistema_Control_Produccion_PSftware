# Alcance del proyecto (1 pagina)

## 1. Proposito del proyecto

Disenar una propuesta academica de arquitectura para un Sistema de Control de Produccion (MES) del caso #17, demostrando el uso correcto de patrones de diseno en Python.

## 2. Problema que resuelve

En un MES industrial aparecen retos de diseno que afectan mantenibilidad y consistencia:

- Coordinacion central del estado global del sistema.
- Creacion extensible de tipos de maquina sin acoplar el cliente.
- Integracion de componentes con interfaces incompatibles.
- Construccion ordenada de objetos complejos (reportes).
- Coherencia entre familias de componentes de una linea de produccion.

## 3. Usuarios objetivo

- Docente evaluador de la asignatura de Patrones de Software.
- Estudiantes del equipo que presentan analisis, UML y codigo.
- Compañeros que revisan ejemplos practicos de patrones aplicados a un caso MES.

## 4. Alcance funcional (si incluye)

El proyecto SI incluye una implementacion conceptual y demostrativa de:

1. `Singleton` para controlador central (`MESController`).
2. `Factory Method` para creacion de maquinas (`CNCFactory`, `RobotFactory`).
3. `Abstract Factory` para familias de linea de produccion compatibles.
4. `Builder` para ensamblar reportes de produccion por pasos.
5. `Adapter` para integrar un gateway legacy con interfaz moderna.
6. `Prototype` para clonar plantillas de orden de produccion.
7. Diagramas UML por patron y vista general del diseno.
8. Tests conceptuales por patron y ejecucion conjunta con `test_PARCIAL.py`.

## 5. Fuera de alcance (no incluye)

Este proyecto NO incluye:

- Desarrollo completo de un MES productivo.
- Interfaz web o aplicacion movil.
- Persistencia en base de datos.
- Integracion real con PLC, CNC, robots o equipos fisicos.
- Protocolos industriales en tiempo real (OPC UA, Modbus, etc.).
- Seguridad industrial, ciberseguridad o despliegue en planta.
- KPIs operativos conectados a datos reales de produccion.

## 6. Entregables

1. Documentos de analisis por patron en `Patrones/docs/`.
2. Diagramas UML en `Patrones/docs/diagrams/`.
3. Codigo Python demostrativo en `Patrones/src/`.
4. Pruebas conceptuales por patron en `Patrones/src/test_*.py`.
5. Evidencia de ejecucion agrupada con `Patrones/src/test_PARCIAL.py`.

## 7. Criterios de exito

El proyecto se considera exitoso si:

1. Cada patron aplicado resuelve un problema de diseno claramente descrito.
2. Los diagramas UML son coherentes con la estructura del codigo.
3. Los tests conceptuales ejecutan sin error en entorno local.
4. La documentacion diferencia con claridad el alcance y el fuera de alcance.
5. El lector puede responder en menos de 1 minuto: "que hace" y "que no hace" el proyecto.

## 8. Declaracion breve para presentacion

"Este proyecto no implementa un MES industrial completo. Presenta una solucion academica y demostrativa para el caso #17, aplicando patrones de diseno (Singleton, Factory Method, Abstract Factory, Builder, Adapter y Prototype) con UML, codigo Python y pruebas conceptuales."
