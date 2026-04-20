# 12. Patron Facade aplicado al MES

## 12.1 Problema

Iniciar una orden de produccion en el MES requiere coordinar varios subsistemas:

- Validacion de orden
- Reserva de materiales
- Preparacion de linea
- Configuracion de calidad
- Apertura de trazabilidad

Si el operador invoca cada subsistema manualmente, se produce:

- Acoplamiento del cliente con demasiados componentes internos
- Mayor riesgo de secuencias incompletas o incorrectas
- Dificultad para mantener y evolucionar el flujo de inicio

## 12.2 Solucion (aplicacion del patron)

Se aplica **Facade** para exponer un punto unico de arranque de orden.

### Elementos del patron en este caso

- **Facade:** `MESProductionFacade`
- **Subsystems:** `OrderValidator`, `InventoryService`, `MachinePreparationService`, `QualityService`, `TrackingService`
- **Client:** `MESOperatorConsole`

El cliente llama `start_order(...)` y la fachada coordina internamente todo el flujo.

## 12.3 Justificacion

Facade se justifica porque:

- Simplifica el uso del MES para clientes operativos
- Reduce acoplamiento entre cliente y subsistemas tecnicos
- Centraliza reglas de secuencia del proceso de inicio

## 12.4 Evidencia del patron

Para evidenciar Facade se usa:

- Metodo `start_order()` que orquesta todos los subsistemas
- Respuesta unificada de exito/error para el cliente

**UML:** `Patrones/docs/diagrams/facade.puml`  
**Python conceptual:** `Patrones/src/facade_m.py`

## 12.5 Consideraciones

- Facade no reemplaza subsistemas; solo simplifica su consumo.
- Conviene mantener la fachada enfocada en flujos de alto nivel.
- En este ejercicio se usa una implementacion didactica y conceptual.
