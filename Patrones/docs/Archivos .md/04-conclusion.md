# 4. Conclusiones

En el caso del Sistema de Control de Producción (MES) se aplicaron dos patrones de diseño con objetivos específicos:

## Singleton

Se aplicó al `MESController` para garantizar:

- Un único punto de coordinación del sistema
- Consistencia en el estado global
- Control centralizado de planificación y métricas (OEE)

Esto evita duplicidad de instancias y posibles inconsistencias.

## Factory Method

Se aplicó para la creación de máquinas industriales (CNC y Robot) con el fin de:

- Reducir acoplamiento a clases concretas
- Facilitar la extensión del sistema
- Cumplir el principio Open/Closed

## Evidencia presentada

La aplicación conceptual de los patrones se respalda mediante:

- Análisis del problema
- Justificación de diseño
- Diagramas UML
- Implementación estructural en Python

Aunque no se desarrolló un sistema funcional completo, la estructura evidencia claramente la utilización correcta de los patrones.