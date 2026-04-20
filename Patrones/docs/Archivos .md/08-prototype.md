# 8. Patron Prototype aplicado al MES

## 8.1 Definicion del patron

El patron **Prototype** permite crear nuevos objetos clonando una instancia existente (prototipo), en lugar de construirlos desde cero.

Su objetivo es reutilizar configuraciones base y acelerar la creacion de objetos similares.

## 8.2 Problema

En el MES es comun generar muchas ordenes de produccion con configuraciones repetidas:

- Perfil de maquina por tipo de linea.
- Parametros estandar de operacion.
- Lista base de controles de calidad.

Si cada orden se arma manualmente desde cero, aumenta:

- Duplicacion de codigo y datos.
- Riesgo de inconsistencias en configuracion.
- Costo de mantenimiento al cambiar plantillas.

## 8.3 Justificacion en el caso MES

Prototype se justifica porque:

- Permite clonar una plantilla de orden ya validada.
- Reduce tiempo para preparar nuevas ordenes operativas.
- Mantiene consistencia entre ordenes del mismo tipo.
- Facilita ajustes locales en el clon sin afectar la plantilla original.

## 8.4 Estructura del patron

Aplicacion en este caso:

- **Prototype:** `Prototype`
- **Concrete Prototype:** `ProductionOrderTemplate`
- **Client/Registry:** `TemplateRegistry`
- **Cliente de negocio:** `MESProductionPlanner`

El patron se implementa con clonacion profunda (`deepcopy`) para evitar que estructuras anidadas del clon compartan referencia con la plantilla base.

**UML:** `Patrones/docs/diagrams/prototype.puml`  
**Python conceptual:** `Patrones/src/prototype_m.py`

## 8.5 Explicacion de resultados

Con la prueba conceptual:

- Se registra una plantilla base (`cnc_standard`) en el `TemplateRegistry`.
- El planificador solicita un clon para una orden concreta.
- Se personaliza el clon (orden, turno, unidades y parametros).
- Se valida que cambios del clon no alteran la plantilla original.

Esto evidencia reutilizacion de configuraciones con independencia entre objeto base y objeto clonado.

## 8.6 Conclusion

Prototype es adecuado en el MES cuando existen configuraciones de orden recurrentes que deben replicarse de forma rapida y consistente.

En este ejercicio, el patron mejora mantenibilidad y velocidad de preparacion, manteniendo un enfoque academico y demostrativo.
