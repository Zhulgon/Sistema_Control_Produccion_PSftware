# 3. Patrón Factory Method aplicado al MES

## 3.1 Problema

El MES integra diferentes equipos industriales (por ejemplo: CNC y robots). Cada tipo puede requerir:

- Configuración distinta
- Inicialización distinta
- Comportamiento distinto

Si el sistema crea máquinas usando condicionales repetidos (if/else o switch por tipo), se genera:

- Acoplamiento fuerte a clases concretas
- Dificultad para extender el sistema
- Cambios frecuentes sobre código existente (mayor riesgo de errores)

## 3.2 Solución (aplicación del patrón)

Se aplica **Factory Method** para encapsular la creación de máquinas.

### Elementos del patrón en este caso

- **Product:** `Machine` (máquina genérica)
- **Concrete Products:** `CNCMachine`, `RobotMachine`
- **Creator:** `MachineFactory` con el método `create_machine()`
- **Concrete Creators:** `CNCFactory`, `RobotFactory`

El resto del sistema usa `MachineFactory` sin depender de clases concretas.

## 3.3 Justificación

Factory Method permite:

- Crear objetos sin acoplar el sistema a implementaciones concretas
- Agregar nuevos tipos de máquinas sin modificar código existente (Open/Closed)
- Separar la lógica de creación de la lógica de uso

## 3.4 Evidencia del patrón

**UML:** `Patrones/docs/diagrams/factory-method.puml`  
**Python conceptual:** `Patrones/src/factory_machines.py`

## 3.5 Extensión

Si se agrega un nuevo equipo (ej: `LaserCutterMachine`), se crea:

- `LaserCutterMachine`
- `LaserCutterFactory`

sin modificar fábricas anteriores ni el flujo general.