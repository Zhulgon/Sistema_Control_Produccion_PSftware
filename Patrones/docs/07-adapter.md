# 7. Patrón Adapter aplicado al MES

## 7.1 Definición del patrón

El patrón **Adapter** permite que dos clases con interfaces incompatibles trabajen juntas.

Su función principal es traducir una interfaz existente (legacy o externa) hacia la interfaz esperada por el cliente actual.

## 7.2 Problema

En un entorno MES, es común integrar componentes legacy con formatos distintos para enviar datos de producción.

En este caso, el módulo moderno del MES espera reportar unidades con una interfaz estándar (`report_units`), pero el gateway legacy recibe datos con otra firma (`send_production_data`) y otro formato de campos.

Sin Adapter, el cliente debería conocer detalles internos del sistema legacy y convertir datos en múltiples puntos del código.

## 7.3 Justificación en el caso MES

Adapter se justifica porque:

- Permite integrar sistemas legacy sin modificar su código fuente.
- Reduce acoplamiento entre el cliente MES y el formato antiguo de integración.
- Centraliza la traducción de datos (orden, línea y cantidad) en una sola clase.
- Facilita mantenimiento y evolución de integraciones industriales.

## 7.4 Estructura del patrón

Aplicación en este caso:

- **Target:** `ProductionTrackingService`
- **Adaptee:** `LegacyMachineGateway`
- **Adapter:** `LegacyMachineAdapter`
- **Client:** `MESProductionClient`

Se usa **Adapter por composición** (object adapter), que es la variante más flexible en práctica.

**UML:** `Patrones/docs/diagrams/adapter.puml`  
**Python conceptual:** `Patrones/src/adapter_m.py`

## 7.5 Explicación de resultados

Con la prueba conceptual:

- El cliente llama `close_partial_report(...)` usando la interfaz moderna.
- El Adapter transforma el `order_id` y `production_line` al formato legacy.
- El Adaptee procesa el mensaje sin que el cliente conozca su contrato interno.

Esto evidencia traducción de interfaces y desacoplamiento entre sistemas incompatibles.

## 7.6 Conclusión

Adapter es adecuado cuando el MES debe conectarse con componentes externos o legacy sin reescribirlos.

En este ejercicio, el patrón permite mantener una interfaz clara para el cliente moderno y encapsular la adaptación técnica en una capa específica, con enfoque académico y demostrativo.
