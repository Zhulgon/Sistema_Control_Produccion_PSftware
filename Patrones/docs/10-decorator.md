# 10. Patron Decorator aplicado al MES

## 10.1 Problema

El MES genera reportes de cierre de turno con un bloque base comun, pero segun la necesidad operativa puede requerir:

- Controles de calidad.
- Datos de trazabilidad.
- Indicador OEE.

Si se crean subclases para cada combinacion, se produce:

- Multiplicacion de clases (`ReporteConCalidad`, `ReporteConCalidadYOEE`, etc.).
- Rigidez para agregar o quitar capacidades.
- Mayor acoplamiento en la construccion de reportes.

## 10.2 Solucion (aplicacion del patron)

Se aplica **Decorator** para envolver el reporte base y agregar responsabilidades de forma incremental.

### Elementos del patron en este caso

- **Component:** `ProductionReport`
- **Concrete Component:** `BaseProductionReport`
- **Decorator base:** `ReportDecorator`
- **Concrete Decorators:** `QualityDecorator`, `TraceabilityDecorator`, `OEEDecorator`

El cliente compone decoradores segun la necesidad del turno.

## 10.3 Justificacion

Decorator se justifica porque:

- Permite agregar capacidades sin modificar la clase base.
- Evita explosion de subclases por combinaciones de funcionalidades.
- Mantiene el principio Open/Closed en la evolucion del reporte.

## 10.4 Evidencia del patron

Para evidenciar Decorator se usa:

- Encadenamiento de decoradores sobre `BaseProductionReport`.
- Resultado final enriquecido segun el orden de composicion.

**UML:** `Patrones/docs/diagrams/decorator.puml`  
**Python conceptual:** `Patrones/src/decorator_m.py`

## 10.5 Consideraciones

- El orden de decoracion puede influir en algunos resultados.
- Conviene mantener decoradores pequenos y con una sola responsabilidad.
- En este ejercicio se usa una implementacion didactica para mostrar composicion dinamica.
