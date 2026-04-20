# 11. Patron Composite aplicado al MES

## 11.1 Problema

El MES necesita representar la capacidad de produccion en diferentes niveles:

- Planta
- Linea
- Maquina

Si el sistema trata por separado cada nivel con logica distinta, aparecen:

- Condicionales repetidos para recorrer estructura
- Duplicidad de calculos de capacidad
- Mayor complejidad para escalar la jerarquia

## 11.2 Solucion (aplicacion del patron)

Se aplica **Composite** para tratar de forma uniforme elementos simples y compuestos.

### Elementos del patron en este caso

- **Component:** `ProductionNode`
- **Leaf:** `MachineStation`
- **Composite:** `ProductionGroup`
- **Client:** `MESCapacityService`

El cliente calcula capacidad y estructura sin distinguir si el nodo es maquina o grupo.

## 11.3 Justificacion

Composite se justifica porque:

- Permite recorrer la estructura de planta de manera recursiva y uniforme
- Facilita agregar nuevos niveles sin reescribir la logica del cliente
- Mejora mantenibilidad al centralizar operaciones de agregacion y calculo

## 11.4 Evidencia del patron

Para evidenciar Composite se usa:

- Metodo uniforme `total_planned_units()` para hoja y compuesto
- Metodo `summary()` recursivo para exportar estructura de arbol

**UML:** `Patrones/docs/diagrams/composite.puml`  
**Python conceptual:** `Patrones/src/composite_m.py`

## 11.5 Extension

Si se agrega un nuevo nivel (ej: `AreaProductionGroup`), el cliente puede seguir calculando capacidad total sin cambios en su flujo.
