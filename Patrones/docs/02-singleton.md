# 2. Patrón Singleton aplicado al MES

## 2.1 Problema

El MES necesita un componente central que coordine y mantenga consistencia en:

- Programación de producción
- Estado global de ejecución
- Trazabilidad de eventos
- Métricas globales como OEE

Si existieran varias instancias de ese coordinador, podrían generarse decisiones contradictorias (por ejemplo, dos programaciones simultáneas o dos estados distintos del mismo proceso).

## 2.2 Solución (aplicación del patrón)

Se aplica **Singleton** al componente central del sistema:

**Clase candidata:** `MESController`

Este controlador debe existir como **una única instancia** durante la ejecución del sistema, actuando como punto de coordinación y referencia del estado global.

## 2.3 Justificación

Se justifica Singleton porque:

- El control del MES debe ser único para evitar inconsistencias
- Centraliza la coordinación de módulos (planificación, calidad, trazabilidad, OEE)
- Reduce duplicidad de estado y reglas de control

## 2.4 Evidencia del patrón

Para evidenciar Singleton se usa:

- Atributo de clase para almacenar la única instancia
- Control de creación de instancia retornando siempre la misma referencia

**UML:** `Patrones/docs/diagrams/singleton.puml`  
**Python conceptual:** `Patrones/src/singleton_mes_controller.py`

## 2.5 Consideraciones

- Singleton puede concentrar demasiadas responsabilidades si no se controla su alcance.
- En sistemas reales se complementa con separación por servicios e inyección de dependencias.
- En este ejercicio se utiliza por claridad didáctica y porque el MES requiere coordinación central única.