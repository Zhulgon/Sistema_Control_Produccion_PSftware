# Parcial Semana 6 - Patrones de Diseño en MES

## 1. Proyecto general

### 1.1 Contexto

El proyecto corresponde al caso **#17 Sistema de Control de Producción (MES)** del sector industrial.

### 1.2 Objetivo del proyecto

Diseñar de forma académica un modelo base de software para un MES que permita:

- Planificación y programación de producción
- Control de calidad y trazabilidad
- Integración con máquinas CNC y robots
- Seguimiento de métricas OEE

El objetivo no es construir una plataforma industrial real, sino demostrar decisiones correctas de diseño usando patrones creacionales.

### 1.3 Alcance técnico

La evidencia se construye con:

- Documentación de análisis por patrón
- Diagramas UML de estructura
- Código conceptual en Python
- Pruebas de ejecución simples en terminal

### 1.4 Fuera de alcance

- Base de datos y persistencia
- Interfaz gráfica de usuario
- Comunicación con equipos físicos de planta
- Reglas completas de negocio industrial

## 2. Patrón Singleton

### 2.1 Problema en el MES

Un MES necesita un punto central para coordinar estado global. Si existen dos controladores diferentes, se pueden producir decisiones contradictorias sobre la misma orden de producción.

### 2.2 Estructura del patrón en el proyecto

- **Singleton class:** `MESController`
- **Atributo de control:** `_instance`
- **Método clave:** `__new__` para controlar creación

### 2.3 Explicación del bloque de código

En `singleton_mes_controller.py`, la clase define `_instance = None`.  
Cuando se invoca `MESController()`, el método `__new__` revisa si `_instance` es `None`.

- Si es `None`, crea el objeto con `super().__new__(cls)` y lo guarda.
- Si ya existe, retorna la misma referencia.

Esto garantiza que, aunque el cliente llame al constructor varias veces, siempre obtenga la misma instancia lógica del controlador central.

### 2.4 Evidencia funcional y lectura del resultado

- Código: `Patrones/src/singleton_mes_controller.py`
- Test: `Patrones/src/test_singleton.py`

El test crea dos variables (`a` y `b`) y valida `a is b`.  
Además imprime `id(a)` e `id(b)`, que deben ser iguales. Eso prueba el comportamiento Singleton.

### 2.5 Aporte al MES

Evita duplicidad de estado global y centraliza decisiones de coordinación del sistema.

## 3. Patrón Factory Method

### 3.1 Problema en el MES

El sistema debe crear distintos tipos de máquina (por ejemplo, CNC y Robot). Si la creación se hace con `if/else` en muchas partes, aumenta el acoplamiento y el costo de cambio.

### 3.2 Estructura del patrón en el proyecto

- **Product:** `Machine`
- **Concrete Products:** `CNCMachine`, `RobotMachine`
- **Creator:** `MachineFactory`
- **Concrete Creators:** `CNCFactory`, `RobotFactory`

### 3.3 Explicación del bloque de código

En `factory_machines.py`:

- `Machine` define la interfaz común `start()`.
- Cada producto concreto (`CNCMachine`, `RobotMachine`) implementa esa interfaz.
- `MachineFactory` declara `create_machine()` como método abstracto.
- `start_machine()` usa `create_machine()` sin conocer clase concreta.
- `CNCFactory` y `RobotFactory` implementan `create_machine()` retornando el producto correspondiente.

La clave del patrón es que el cliente opera con la abstracción `MachineFactory`, no con constructores concretos directos.

### 3.4 Evidencia funcional y lectura del resultado

- Código: `Patrones/src/factory_machines.py`
- Test: `Patrones/src/test_factory_method.py`

El test instancia cada fábrica y verifica con `isinstance` que:

- `CNCFactory` produce `CNCMachine`
- `RobotFactory` produce `RobotMachine`

La salida confirma que cada creador concreto encapsula la lógica de creación correcta.

### 3.5 Aporte al MES

Permite crecer en nuevos equipos sin tocar el cliente principal, mejorando extensibilidad y mantenibilidad.

## 4. Patrón Abstract Factory

### 4.1 Problema en el MES

No solo se crea un objeto aislado. Una línea productiva requiere **familias compatibles** (máquina + robot/operador). Mezclar familias incorrectas genera inconsistencia de configuración.

### 4.2 Estructura del patrón en el proyecto

- **Abstract Factory:** `ProductionLineFactory`
- **Concrete Factories:** `AutomaticLineFactory`, `ManualLineFactory`
- **Abstract Products:** `Machine`, `Robot`
- **Concrete Products:** `CNCMachine`, `ManualMachine`, `IndustrialRobot`, `HumanOperator`

### 4.3 Explicación del bloque de código

En `abstract_factory_production.py`:

- Se definen productos abstractos (`Machine`, `Robot`) con comportamientos base (`operate`, `assist`).
- Cada producto concreto implementa ese comportamiento.
- `ProductionLineFactory` obliga a implementar `create_machine()` y `create_robot()`.
- `AutomaticLineFactory` devuelve la familia automática (`CNCMachine` + `IndustrialRobot`).
- `ManualLineFactory` devuelve la familia manual (`ManualMachine` + `HumanOperator`).

El cliente obtiene componentes compatibles entre sí porque provienen de la misma fábrica concreta.

### 4.4 Evidencia funcional y lectura del resultado

- Código: `Patrones/src/abstract_factory_production.py`
- Test: `Patrones/src/test_abstract_factory.py`

El test crea ambas fábricas y valida textos de salida:

- Línea automática: `"CNC Machine operating"` + `"Industrial robot assisting"`
- Línea manual: `"Manual machine operating"` + `"Human operator assisting"`

Con ello se confirma la creación de familias consistentes.

### 4.5 Aporte al MES

Asegura coherencia de configuración por tipo de línea y facilita ampliar nuevas líneas en el futuro.

## 5. Patrón Builder

### 5.1 Problema en el MES

`ProductionReport` posee muchos campos y partes opcionales (alertas, notas, datos de salida). Un constructor único extenso afecta legibilidad y mantenimiento.

### 5.2 Estructura del patrón en el proyecto

- **Product:** `ProductionReport`
- **Builder:** `ProductionReportBuilder`
- **Concrete Builder:** `StandardProductionReportBuilder`
- **Director:** `ReportDirector`

### 5.3 Explicación del bloque de código

En `builder_production_report.py`:

- `ProductionReport` es el objeto final (producto) con campos de orden, línea, turno, producción, paradas, alertas y notas.
- `ProductionReportBuilder` define pasos abstractos: `reset`, `set_header`, `set_output`, `add_quality_alert`, `set_operator_notes`, `build`.
- `StandardProductionReportBuilder` implementa esos pasos y mantiene un estado interno `_report`.
- `build()` retorna el reporte construido y reinicia el builder para próxima construcción.
- `ReportDirector` define secuencias de ensamblaje:
  - `build_standard_shift_report(...)`
  - `build_report_with_alerts(...)`

Esto separa claramente la lógica de ensamblaje (Director/Builder) del uso final del objeto.

### 5.4 Evidencia funcional y lectura del resultado

- Código: `Patrones/src/builder_production_report.py`
- Test: `Patrones/src/test_builder.py`

El test construye dos reportes:

- Uno estándar (sin alertas)
- Uno con alertas de calidad

Valida que:

- El primer reporte tiene `quality_alerts == []`
- El segundo contiene dos alertas

Así se demuestra construcción paso a paso con variantes controladas.

### 5.5 Aporte al MES

Permite crear reportes complejos de forma ordenada, escalable y con menor acoplamiento.

## 6. Evidencias de ejecución

Desde `Patrones/src`:

```bash
python test_singleton.py
python test_factory_method.py
python test_abstract_factory.py
python test_builder.py
python run_parcial_tests.py
```

`run_parcial_tests.py` ejecuta todos los tests y muestra el estado individual por patrón.

## 7. Conclusión

La propuesta integra una vista completa del proyecto MES y la aplicación coherente de patrones creacionales.

Cada patrón se eligió por una necesidad concreta:

- Singleton: control global único
- Factory Method: creación desacoplada de tipos de máquina
- Abstract Factory: familias compatibles de componentes
- Builder: construcción gradual de objetos complejos

Con pruebas funcionales mínimas, UML y documentación, el trabajo cumple propósito académico con evidencia verificable.
