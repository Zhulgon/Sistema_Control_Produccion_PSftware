# 5. Patrón Builder aplicado al MES

## 5.1 Definición del patrón

El patrón **Builder** separa la construcción de un objeto complejo de su representación final.

Su objetivo es construir el objeto en pasos, permitiendo diferentes variantes de construcción sin cambiar el proceso general.

## 5.2 Problema

En el MES, los reportes de producción pueden requerir múltiples bloques de información:

- Encabezado de orden y línea
- Resultado de producción (planificado vs producido)
- Tiempos de parada
- Alertas de calidad
- Notas del operador

Si se crea `ProductionReport` con un constructor largo o múltiples variantes de inicialización, el código se vuelve difícil de mantener y propenso a errores de configuración.

## 5.3 Justificación en el caso MES

Builder se justifica porque:

- Permite construir reportes de forma incremental y clara
- Evita constructores extensos con demasiados parámetros
- Facilita generar variantes de reporte (estándar o con incidencias) reutilizando el mismo flujo base
- Reduce acoplamiento entre quien usa el reporte y la forma exacta de construirlo

## 5.4 Estructura del patrón

Aplicación en este caso:

- **Product:** `ProductionReport`
- **Builder:** `ProductionReportBuilder` (interfaz abstracta)
- **Concrete Builder:** `StandardProductionReportBuilder`
- **Director:** `ReportDirector`

El `Director` define secuencias de construcción, mientras que el `Concrete Builder` arma el objeto paso a paso.

**UML:** `Patrones/docs/diagrams/builder.puml`  
**Python conceptual:** `Patrones/src/builder_production_report.py`

## 5.5 Explicación de resultados

Con la implementación conceptual:

- Se construye un reporte estándar de turno con una secuencia fija
- Se construye un reporte con alertas de calidad agregando pasos opcionales
- El cliente no manipula la construcción interna del producto final

Esto demuestra una creación controlada, legible y extensible para objetos complejos del dominio MES.

## 5.6 Conclusión

Builder es adecuado para el MES cuando se requiere ensamblar objetos de reporte con múltiples partes opcionales.

En este ejercicio, el patrón mejora la claridad del proceso de construcción y mantiene separada la lógica de ensamblaje respecto del uso del reporte, conservando un enfoque académico y conceptual.
